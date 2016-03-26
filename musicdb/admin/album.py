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
from .views import AlbumFromPathView, AlbumRecalculateRGView


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

    # list_editable = ('source_id',)
    list_display = ('artist', 'date', 'title', 'add_time', 'is_available', 'track_count', 'has_tracklisting')
    list_filter = ('is_available', 'is_deleted', 'source', 'genre')

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
                'artist', 'title', 'is_available', 'is_deleted', 'date',
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

    def get_queryset(self, request):
        qs = super(self.__class__, self).get_queryset(request)
        qs = qs.annotate(django_models.Count('track', distinct=True))
        qs = qs.annotate(
                back_covers_count=django_models.Count(
                    django_models.Case(
                        django_models.When(
                            (django_models.Q(cover__covertype=models.Cover.COVER_TYPE_BACK_OUT) |
                                django_models.Q(cover__covertype=models.Cover.COVER_TYPE_OUT)),
                            then=1,
                        )
                    ), distinct=True)
        )
        return qs

    def get_urls(self):
        urls = super(AlbumAdmin, self).get_urls()
        custom_urls = [
                url('^addbypath/$',
                    self.admin_site.admin_view(AlbumFromPathView.as_view()), name='musicdb_album_addbypath'),
                url('^(?P<pk>\d+)/recalculate_rg/$', self.admin_site.admin_view(
                    AlbumRecalculateRGView.as_view()), name='musicdb_album_recalculate_replaygain')
        ]
        return custom_urls + urls

    def has_tracklisting(self, obj):
        return bool(obj.back_covers_count)
    has_tracklisting.admin_order_field = 'back_covers_count'
    has_tracklisting.boolean = True

    def track_count(self, obj):
        return obj.track__count
    track_count.admin_order_field = 'track__count'

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
        init_path = data.get('path')

        if (init_path):
            same_path_albums = models.Album.objects.filter(path=init_path)
            filenames = []
            if init_path and same_path_albums.count() == 0:
                abs_path = settings.MUSIC_LIBRARY_PATH + init_path
                if os.path.isdir(abs_path) and os.path.exists(abs_path):
                    for root, dirs, files in os.walk(abs_path):
                        for file in files:
                            if file.endswith(".flac"):
                                filenames.append(audiotools.Filename.from_unicode(os.path.join(root, file)))
            album_initial = {}
            self.tracks_initial = []
            artists = []
            for track in audiotools.open_files(filenames):
                track_meta = track.get_metadata()
                album_initial['title'] = track_meta.album_name
                if track_meta.year:
                    try:
                        album_initial['date'] = datetime.date(int(track_meta.year), 1, 1)
                    except ValueError:
                        pass
                if track_meta.artist_name:
                    artists.append(track_meta.artist_name)
                self.tracks_initial.append({
                    'path': os.path.relpath(
                        track.filename.decode('UTF-8'), settings.MUSIC_LIBRARY_PATH + init_path),
                    'track_num': track_meta.track_number,
                    'track_artist': track_meta.artist_name,
                    'title': track_meta.track_name
                })

            from collections import Counter
            artists_counter = Counter(artists)
            album_artist = None
            most_common_artist = artists_counter.most_common(1)
            if len(most_common_artist) and most_common_artist[0][1] > len(self.tracks_initial) / 2:
                album_artist = most_common_artist[0][0]

            if album_artist:
                if not album_initial.get('artist'):
                    try:
                        album_initial['artist'] = models.Artist.objects.get(name__iexact=album_artist)
                    except models.Artist.DoesNotExist:
                        pass

            for track_initial in self.tracks_initial:
                if track_initial['track_artist'] == album_artist:
                    del track_initial['track_artist']

            data.update(album_initial)

        return data

    def changeform_view(self, *args, **kwargs):
        self.tracks_initial = []
        return super(self.__class__, self).changeform_view(*args, **kwargs)

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
                else:
                    initials = super(AlbumAdmin, self).get_changeform_initial_data(request)
                    path = initials.get('path')

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
