from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.db import models as django_models
from . import models
import os


class AlbumPathField(forms.FilePathField):

        def filterchoices(self, choice):
                k, v = choice
                if not k:
                        return True
                result = bool(
                    filter(lambda x: x.endswith('.flac'),
                           os.listdir(k)))
                return result

        def __init__(self, *args, **kwargs):
                super(AlbumPathField, self).__init__(*args, **kwargs)
                self.choices = filter(self.filterchoices, self.choices)
                self.choices = sorted(self.choices, key=lambda x: x[1])
                self.widget.choices = self.choices


class TrackPathField(forms.FilePathField):

        def __init__(self, *args, **kwargs):
                super(TrackPathField, self).__init__(*args, **kwargs)
                self.choices = sorted(self.choices, key=lambda x: x[1])
                self.widget.choices = self.choices


class TrackInline(admin.TabularInline):
        formfield_overrides = {
            django_models.FilePathField: {'form_class': TrackPathField}
        }
        model = models.Track
        can_delete = False
        extra = 0
        readonly_fields = ('length', 'rg_peak', 'rg_gain')
        exclude = ('lirycs',)

        def has_add_permission(self, request):
                return False


class CoverInline(admin.TabularInline):
        fields = ('thumb', 'cover', 'covertype', 'sort')
        readonly_fields = ('thumb',)
        model = models.Cover

        def thumb(self, obj):
                return format_html(
                    """
            <a href="{0}">
                <img src="{0}" style="max-width: 150px; max-height: 150px">
            </a>
            """, obj.cover.url, None)
        thumb.allow_tags = True


class AlbumAdmin(admin.ModelAdmin):
        readonly_fields = ('rg_peak', 'rg_gain', 'add_time')
        fieldsets = (
            (None, {
                'fields': (
                    'artist', 'title', 'is_available', 'date',
                    'add_time', 'active_from', 'path',
                    'genre', 'mbid'
                )
            }),
            ('Edition', {
                'classes': ('collapse',),
                'fields': (
                    ('release_type', 'label', 'release_date'),
                    ('edition_title', 'catalog_num', 'barcode'),
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
        inlines = [
            CoverInline,
            TrackInline
        ]

        def __init__(self, *args, **kwargs):
                self.formfield_overrides = {
                    django_models.FilePathField: {'form_class': AlbumPathField}
                }
                return super(AlbumAdmin, self).__init__(*args, **kwargs)

        def get_inline_instances(self, request, obj=None):
            instances = super(AlbumAdmin, self).get_inline_instances(
                request, obj)
            for instance in instances:
                if isinstance(instance, TrackInline):
                    if obj and obj.path:
                        instance.formfield_overrides[
                            django_models.FilePathField]['path'] = obj.path
                    else:
                        instance.formfield_overrides[
                            django_models.FilePathField].pop('path', None)
            return instances


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
