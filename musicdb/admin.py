import os
import re

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.db import models as django_models
from django.core.cache import cache
from django_select2.forms import Select2Widget, Select2MultipleWidget
from django.utils.http import urlquote
from django.utils.translation import ugettext as _


from . import models


class RelativeSortedFilePathField(forms.FilePathField):
    def __init__(self, *args, **kwargs):
        super(RelativeSortedFilePathField, self).__init__(*args, **kwargs)
        choices = self.choices
        for i, x in enumerate(choices):
            if x[0]:
                self.choices[i] = (x[1], x[1])
        self.choices = sorted(choices, key=lambda x: x[1])


class AlbumPathField(RelativeSortedFilePathField):
    re_disk_subdir = re.compile(r"(^|\/)cd[\d]+/?$", re.IGNORECASE)

    def filterchoices(self, choice):
        k, v = choice
        if not k:
            return True
        if re.search(self.re_disk_subdir, k):
            return False

        result = bool(
            filter(
                (lambda x: x.endswith('.flac') or
                    re.match(self.re_disk_subdir, x)),
                os.listdir(self.path + k)))
        return result

    def __init__(self, *args, **kwargs):
        choices_cache_key = self.__class__.__name__ + '.choices'
        choices = cache.get(choices_cache_key)
        if not choices:
            super(AlbumPathField, self).__init__(*args, **kwargs)
            choices = self.choices
            choices = filter(self.filterchoices, choices)
            choices = sorted(choices, key=lambda x: x[1])
            cache.set(choices_cache_key, choices)
        else:
            acceptable_args = (
                'required', 'widget', 'label', 'initial', 'help_text',
                'error_messages', 'show_hidden_initial', 'validators',
                'localize', 'label_suffix',
            )
            new_kwargs = {
                k: v for k, v in kwargs.iteritems() if k in acceptable_args}
            super(forms.FilePathField, self).__init__(
                choices=(), *args, **new_kwargs)
        self.choices = choices
        self.widget.choices = self.choices


class TrackInline(admin.TabularInline):
        formfield_overrides = {
            django_models.FilePathField: {
                'form_class': RelativeSortedFilePathField}
        }
        model = models.Track
        can_delete = False
        extra = 0
        readonly_fields = ('path', 'length', 'rg_peak', 'rg_gain')
        exclude = ['lirycs', ]

        def has_add_permission(self, request):
                return False


class CoverInline(admin.TabularInline):
        fields = ('thumb', 'cover', 'covertype', 'sort')
        readonly_fields = ('thumb',)
        model = models.Cover
        ordering = ('covertype', 'sort')

        def thumb(self, obj):
            return format_html(
                """
                <a href="{0}">
                    <img src="{0}" style="max-width: 150px; max-height: 150px">
                </a>
                """, obj.cover.url, None)
        thumb.allow_tags = True


class AdminAlbumForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(AdminAlbumForm, self).clean()
        source = cleaned_data.get("source")
        source_id = cleaned_data.get("source_id")
        if models.Album.MY_RIP != source and not source_id:
            msg = forms.ValidationError(_("This field is required."))
            self.add_error('source_id', msg)


class AlbumAdmin(admin.ModelAdmin):
    form = AdminAlbumForm
    readonly_fields = ('rg_peak', 'rg_gain', 'add_time',
                       'last_fm', 'musicbrains', 'source_link')

    list_display = ('artist', 'date', 'title', 'is_available')
    # list_editable = ('source_id',)
    list_filter = ('is_available', 'source')

    search_fields = ['artist__name', 'title']

    fieldsets = (
        ('Links', {
            'fields': (
                ('last_fm', 'musicbrains', 'source_link'),
            ),
        }),
        ('Main', {
            'fields': (
                'artist', 'title', 'is_available', 'date',
                'add_time', 'active_from', 'path',
                'genre', 'mbid'
            )
        }),
        ('Edition', {
            'classes': ('collapse',),
            'fields': (
                ('release_type', 'edition_title'),
                ('label', 'catalog_num'),
                ('release_date', 'barcode'),
            )
        }),
        ('Source', {
            'classes': ('collapse',),
            'fields': (('source', 'source_id'), 'comment')
        }),
        ('ReplayGain', {
            'classes': ('collapse',),
            'fields': (('rg_peak', 'rg_gain'), )
        }),
    )
    list_max_show_all = 1000
    ordering = ['artist__name', 'date']
    inlines = [
        CoverInline,
        TrackInline
    ]

    def __init__(self, *args, **kwargs):
        self.formfield_overrides = {
            django_models.FilePathField: {
                'form_class': AlbumPathField,
                'widget': Select2Widget
            },
            django_models.ManyToManyField: {
                'widget': Select2MultipleWidget(attrs={
                    'data-width': 'auto',
                })
            }
        }
        return super(AlbumAdmin, self).__init__(*args, **kwargs)

    def last_fm(self, obj):
        link = \
            '<a href="http://www.last.fm/music/{}/{}">Last.fm</a>'.format(
                urlquote(obj.artist.name.replace(' ', '+')),
                urlquote(obj.title.replace(' ', '+'))
            )
        return link
    last_fm.allow_tags = True

    def musicbrains(self, obj):
        if obj.mbid:
            link = \
                '<a href="http://musicbrainz.org/release/{}">MusicBrains</a>'\
                .format(
                    obj.mbid,
                )
        else:
            link = \
                ('<a href="http://musicbrainz.org/search?type=release_group'
                 '&limit=25&method=advanced&query=artist%3A%22{}%22+AND+%22{}'
                 '%22">Search</a>')\
                .format(
                    urlquote(obj.artist.name.replace(' ', '+')),
                    urlquote(obj.title.replace(' ', '+'))
                )
        return link
    musicbrains.allow_tags = True

    def source_link(self, obj):
        if not obj.source_id:
            return
        if obj.source == models.Album.WHAT_CD:
            link = ('<a href="https://what.cd/torrents.php?torrentid={}">'
                    'what.cd</a>'.format(urlquote(obj.source_id)))
        if obj.source == models.Album.WAFFLES_FM:
            link = ('<a href="https://waffles.fm/details.php?id={}">'
                    'waffles.fm</a>'.format(urlquote(obj.source_id)))
        return link
    source_link.allow_tags = True

    def get_inline_instances(self, request, obj=None):
        instances = super(AlbumAdmin, self).get_inline_instances(
            request, obj)
        for instance in instances:
            if isinstance(instance, TrackInline):
                if obj and obj.path:
                    instance.formfield_overrides[
                        django_models.FilePathField]['path'] = (
                            settings.MUSIC_LIBRARY_PATH + obj.path + '/')
                    instance.exclude = filter(
                        lambda x: x != 'path',
                        instance.exclude
                    )
                else:
                    instance.formfield_overrides[
                        django_models.FilePathField].pop('path', None)
                    instance.exclude.append('path')
        return instances

    class Media:
        css = {
            'all': ('musicdb/admin-album-form.css',)
        }


class PlayLogAdmin(admin.ModelAdmin):
        date_hierarchy = 'time'
        list_display = ('time', 'source', 'track')
        readonly_fields = ('time', 'source', 'track')
        search_fields = ['track__title', 'track__album__title',
                         'track__album__artist__name']
        # radio_fields = {'source': admin.VERTICAL}
        list_filter = (
            'source',
            'track__album'
        )


admin.site.register(models.Artist)
admin.site.register(models.Album, AlbumAdmin)
admin.site.register(models.Track)
admin.site.register(models.Label)
admin.site.register(models.Genre)
admin.site.register(models.PlayLog, PlayLogAdmin)
