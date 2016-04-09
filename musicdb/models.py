# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import path, rename

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# from django.db.models.signals import post_delete, post_save
# from django.dispatch.dispatcher import receiver


class Artist(models.Model):
    artist_id = models.AutoField(primary_key=True, editable=False)

    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta(object):
        ordering = ['name']


class Label(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, db_index=True)
    mbid = models.CharField(max_length=36, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta(object):
        ordering = ['name']


class Release(models.Model):
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    album = models.ForeignKey('Album', on_delete=models.CASCADE)
    catalog_num = models.CharField(max_length=256, blank=True, null=True)


class Genre(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, unique=True)

    def __unicode__(self):
        return self.name

    class Meta(object):
        ordering = ['name']


class Album(models.Model):
    MY_RIP = 0
    WHAT_CD = 1
    WAFFLES_FM = 2
    ALBUM_SOURCES = (
        (MY_RIP, "my"),
        (WHAT_CD, "what.cd"),
        (WAFFLES_FM, "waffles.fm"),
    )
    RELEASE_TYPES = (
        (0, "LP"),
        (1, "EP"),
        (2, "Anthology"),
        (3, "Soundtrack"),
        (4, "Compilation"),
        (5, "Single"),
        (6, "Live"),
    )

    album_id = models.AutoField(primary_key=True, editable=False)
    artist = models.ForeignKey(Artist, blank=False, null=False)

    labels = models.ManyToManyField(Label, blank=True, through=Release)

    genre = models.ManyToManyField(Genre)

    is_available = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    add_time = models.DateTimeField(auto_now_add=True)
    active_from = models.DateField(blank=True, null=True)
    path = models.FilePathField(
        path=unicode(settings.MUSIC_LIBRARY_PATH),
        recursive=True,
        blank=True,
        null=True,
        unique=True,
        allow_files=False,
        allow_folders=True)

    title = models.CharField(max_length=255, db_index=True)
    date = models.DateField(db_index=True)
    release_date = models.DateField(blank=True, null=True)

    barcode = models.CharField(max_length=256, blank=True, null=True)
    source = models.PositiveSmallIntegerField(
        choices=ALBUM_SOURCES, default=1)
    source_id = models.CharField(max_length=256, blank=True, null=True)
    release_type = models.PositiveSmallIntegerField(
        choices=RELEASE_TYPES, default=0)
    comment = models.TextField(blank=True, null=True)
    edition_title = models.CharField(default="Original Release", max_length=256, blank=False, null=True)

    mbid = models.CharField(max_length=36, blank=True, null=True)
    rg_peak = models.FloatField(blank=True, null=True, editable=False)
    rg_gain = models.FloatField(blank=True, null=True, editable=False)

    def __unicode__(self):
        return '%s - %d - %s' % (self.artist,
                                 self.date.year, self.title)

    class Meta(object):
        ordering = ['artist']


def cover_location(instance, filename):
    filename, extension = path.splitext(instance.cover.name)
    location = "{}/covers/{}_{}{}".format(
        instance.album.path, instance.covertype, instance.sort, extension)
    return location


class Cover(models.Model):
    @staticmethod
    def post_delete(sender, instance, *args, **kwargs):
        instance.cover.delete(save=False)

    @staticmethod
    def post_save(sender, instance, created, *args, **kwargs):
        if not created:
            new_filename = Cover._meta.get_field('cover').generate_filename(
                instance, instance.cover)
            if instance.cover != new_filename:
                rename(
                    instance.cover.path, Cover.covers_storage.path(new_filename))
                instance.cover.name = new_filename
                print instance.cover.name
                instance.save()

    COVER_TYPE_BACK_OUT = "back_out"
    COVER_TYPE_FRONT_OUT = "front_out"
    COVER_TYPE_BACK_IN = "back_in"
    COVER_TYPE_FRONT_IN = "front_in"
    COVER_TYPE_DISC = "disc"
    COVER_TYPE_IN = "in"
    COVER_TYPE_OUT = "out"
    COVER_TYPE_BOOKLET = "booklet"
    COVER_TYPE_OTHER = "other"
    COVER_TYPES = (
        (COVER_TYPE_BACK_OUT, "back out"),
        (COVER_TYPE_FRONT_OUT, "front out"),
        (COVER_TYPE_BACK_IN, "back in"),
        (COVER_TYPE_FRONT_IN, "front in"),
        (COVER_TYPE_DISC, "disc"),
        (COVER_TYPE_IN, "in"),
        (COVER_TYPE_OUT, "out"),
        (COVER_TYPE_BOOKLET, "booklet"),
        (COVER_TYPE_OTHER, "other"),
    )

    covers_storage = FileSystemStorage(
        location=settings.MUSIC_LIBRARY_PATH, base_url=settings.MUSIC_LIBRARY_BASE_URL)

    cover_id = models.AutoField(primary_key=True, editable=False)
    album = models.ForeignKey(Album)

    cover = models.ImageField(
        upload_to=cover_location,
        storage=covers_storage,
        max_length=255,
        blank=True,
        null=True)
    covertype = models.CharField(
        max_length=10, choices=COVER_TYPES, blank=False, null=False,
        default="front_out")
    sort = models.PositiveSmallIntegerField(
        blank=False, null=False, default=1)

    class Meta(object):
        unique_together = (
            ('album', 'covertype', 'sort'),
        )


models.signals.post_delete.connect(Cover.post_delete, sender=Cover)
models.signals.post_save.connect(Cover.post_save, sender=Cover)


class Track(models.Model):
    track_id = models.AutoField(primary_key=True, editable=False)
    album = models.ForeignKey(Album)

    track_num = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    track_artist = models.CharField(max_length=255, blank=True, null=True)
    path = models.FilePathField(
        blank=True,
        null=True,
        path=unicode(settings.MUSIC_LIBRARY_PATH),
        recursive=True,
        allow_files=True,
        allow_folders=False,
        match=r".*\.flac$")
    length = models.PositiveIntegerField(null=True)
    disc = models.PositiveSmallIntegerField(default=1)
    lirycs = models.TextField(blank=True, null=True)
    rg_peak = models.FloatField(blank=True, null=True, editable=False)
    rg_gain = models.FloatField(blank=True, null=True, editable=False)

    def get_fullpath(self):
        return '/'.join((settings.MUSIC_LIBRARY_PATH, self.album.path, self.path)).replace('//', '/')

    def __unicode__(self):
        return '%s (%s)' % (self.title, self.album)

    class Meta(object):
        unique_together = (('album', 'track_num', 'disc'), ('path', 'album'))


class PlayLog(models.Model):
    PLAY_SOURCES = (
        (0, "Дома"),
        (1, "С плеера")
    )

    play_log_id = models.AutoField(primary_key=True, editable=False)
    track = models.ForeignKey(Track, null=False)

    time = models.DateTimeField(default=timezone.now)
    source = models.PositiveSmallIntegerField(
        choices=PLAY_SOURCES, blank=False, null=False)
    user = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return '%s - %s' % (self.time, self.track)

    class Meta(object):
        unique_together = (('track', 'time', 'source'),)
        ordering = ['-time']
