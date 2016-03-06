# -*- coding: utf-8 -*-

import hashlib
import os
import stat
import time
import datetime
from errno import ENOENT

from django.core.cache import cache
from django.db.models import Q
from django.conf import settings
from fuse import FuseOSError, LoggingMixIn, Operations
import audiotools

from musicdb import models


class MusicFsEntry(LoggingMixIn, Operations):
    instance = None

    @staticmethod
    def fat_restrict(string):
        restrict_chars = '\/:<>?*|'
        for char in restrict_chars:
            string = string.replace(char, '_')
        return string

    def path(self):
        raise NotImplementedError()

    def get_instance(self):
        return self.instance


class MusicDir(MusicFsEntry):
    inode = 0

    @classmethod
    def from_path(cls, path):
        obj = None
        if len(path) == 0:
            obj = cls()
        elif len(path) == 1:
            album_id = cache.get('fuse-%s-%s' % (cls.__name__, hashlib.md5(path[0].encode('utf-8')).hexdigest()))
            if not album_id:
                parent = cls()
                parent_entries = parent.entries()
                obj = parent_entries.get(path[0])
            else:
                obj = cls(models.Album.objects.get(pk=album_id))

        if not obj:
            raise FuseOSError(ENOENT)
        return obj

    def __init__(self, instance=None):
        self.instance = instance
        if self.instance:
            self.inode = instance.pk

    def path(self):
        if self.instance:
            album = self.instance
            path = self.__class__.fat_restrict(u"%s–%d–%s" % (album.artist.name, album.date.year, album.title))
            cache.set('fuse-%s-%s' % (
                self.__class__.__name__, hashlib.md5(path.encode('utf-8')).hexdigest()), album.pk)
            return path
        else:
            return u""

    def entries(self):
        entries = dict()
        if self.instance:
            tracks = self.instance.track_set.all()
            for track in tracks:
                entry = MusicFile(track)
                entries[entry.path()] = entry
        else:
            albums = models.Album.objects.filter(
                    Q(active_from__lte=datetime.date.today()) | Q(active_from__isnull=True), is_available=True
            ).select_related('artist')
            for album in albums:
                entry = self.__class__(album)
                entries[entry.path()] = entry
        return entries

    def readdir(self, *args):
        entries = self.entries()
        return ['.', '..'] + entries.keys()

    # def opendir(self, *args):
    #     return 5

    def getattr(self, *args):
        attrs = dict({
            'st_ino': self.inode,
            'st_mode': stat.S_IFDIR | 0555,  # mode
            'st_nlink': 1,      # nlink
            'st_uid':  0,       # uid
            'st_gid':  0,       # gid
            'st_size': 1,       # size
            'st_atime': 0,      # int(rand(3600))*86400, #atime
            'st_mtime': 0,      # int(rand(3600))*86400, #mtime
            'st_ctime': 0,       # int(rand(3600))*86400, #ctime
        })
        return attrs


class MusicFile(MusicFsEntry):
    instance = None

    @classmethod
    def from_path(cls, path):
        if len(path) != 2:
            raise FuseOSError(ENOENT)
        dir = MusicDir.from_path((path[0],))
        files = dir.entries()
        return files[path[1]]

    def __init__(self, instance):
        self.instance = instance

    def getattr(self, *args):
        filename = audiotools.Filename.from_unicode(self.abs_path())
        audiofile = audiotools.open_files((filename,))[0]
        current_meta = audiofile.get_metadata()
        # if current_meta.has_block(4):
        #     vorbis_comment = current_meta.get_block(4)

        track = self.instance
        new_meta = audiotools.MetaData(
                track_name=track.title,
                track_number=track.track_num,
                album_name=track.album.title,
                artist_name=track.album.artist.name,
                year=track.album.date.year,
        )
        new_meta = audiotools.flac.FlacMetaData.converted(new_meta)

        statinfo = os.stat(self.abs_path())
        return dict({
            'st_ino': self.instance.pk,      # ino
            'st_mode': stat.S_IFREG | 0444,  # mode
            'st_nlink': 1,      # nlink
            'st_uid':  0,       # uid
            'st_gid':  0,       # gid
            'st_size': statinfo.st_size - current_meta.size() + new_meta.size(),       # size
            'st_atime': 0,      # int(rand(3600))*86400, #atime
            'st_mtime': 0,      # int(rand(3600))*86400, #mtime
            'st_ctime': 0,       # int(rand(3600))*86400, #ctime
        })

    def path(self):
        track = self.instance
        return self.__class__.fat_restrict(u"%02d–%s.flac" % (track.track_num, track.title))

    def abs_path(self):
        return os.path.join(settings.MUSIC_LIBRARY_PATH, self.instance.album.path, self.instance.path)


class Loopback(Operations):
    def __call__(self, op, *args, **kwargs):
        if op == 'init':
            return self.__init__()
        else:
            start = time.time()
            print '-> %s %s' % (op, repr(args))
            path = args[0]
            path_list = filter(lambda x: x != '', path.split('/'))
            if len(path_list) < 2:
                instance = MusicDir.from_path(path_list)
            else:
                instance = MusicFile.from_path(path_list)
            result = instance.__call__(op, *args)
            print time.time() - start
            return result
