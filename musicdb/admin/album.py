import os
import datetime

from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.db import models as django_models
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django_select2.forms import Select2MultipleWidget

import audiotools

from .. import models
from .album_inlines import CoverInline, ReleaseInline, TrackInline
from .fields import AlbumPathField
from .forms import AlbumFromPathForm
from .views import AlbumFromPathView


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
    list_filter = ('is_available', 'source')

    search_fields = ['artist__name', 'title']
    formfield_overrides = {
        django_models.FilePathField: {
            'form_class': AlbumPathField,
        },
        django_models.ManyToManyField: {
            'widget': Select2MultipleWidget(attrs={
                'data-width': 'auto',
            })
        }
    }

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
                # ('label', 'catalog_num'),
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
        ReleaseInline,
        CoverInline,
        TrackInline
    ]

    tracks_initial = []
    initial_path = False

    def get_urls(self):
        urls = super(AlbumAdmin, self).get_urls()
        custom_urls = [
                url('^addbypath/$',
                    self.admin_site.admin_view(AlbumFromPathView.as_view()), name='musicdb_album_addbypath')
        ]
        return custom_urls + urls

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

    def get_changeform_initial_data(self, request):
        data = super(AlbumAdmin, self).get_changeform_initial_data(request)
        same_path_albums = models.Album.objects.filter(path=data['path'])
        # TODO
        filenames = []
        if data['path']:# and same_path_albums.count() == 0:
            self.initial_path = data['path']
            abs_path = settings.MUSIC_LIBRARY_PATH + data['path']
            if os.path.isdir(abs_path) and os.path.exists(abs_path):
                for root, dirs, files in os.walk(abs_path):
                    for file in files:
                        if file.endswith(".flac"):
                            filenames.append(audiotools.Filename.from_unicode(os.path.join(root, file)))
        album_initial = {}
        self.tracks_initial = []
        for track in audiotools.open_files(filenames):
            track_meta = track.get_metadata()
            album_initial['title'] = track_meta.album_name
            if track_meta.year:
                album_initial['date'] = datetime.date(int(track_meta.year), 1, 1)
            if track_meta.artist_name:
                try:
                    album_initial['artist'] = models.Artist.objects.get(name=track_meta.artist_name)
                except models.Artist.DoesNotExist:
                    pass
            self.tracks_initial.append({
                'path': os.path.relpath(track.filename, settings.MUSIC_LIBRARY_PATH + self.initial_path),
                'track_num': track_meta.track_number,
                'title': track_meta.track_name
            })
        data.update(album_initial)
        return data

    def get_inline_instances(self, request, obj=None):
        instances = super(AlbumAdmin, self).get_inline_instances(
            request, obj)
        for instance in instances:
            if isinstance(instance, TrackInline):
                instance.initial = self.tracks_initial
                instance.extra = len(self.tracks_initial)
                path = False
                if obj and obj.path:
                    path = obj.path
                elif self.initial_path:
                    path = self.initial_path
                if path:
                    instance.formfield_overrides[
                        django_models.FilePathField]['path'] = (
                            settings.MUSIC_LIBRARY_PATH + path + '/')
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
