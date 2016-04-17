# -*- coding: utf-8 -*-

import hashlib
import os
import io
import stat
import datetime
import calendar
import random
from errno import ENOENT
from threading import Lock
import StringIO

from django.core.cache import cache
from django.db.models import Q
from django.conf import settings
from django.utils.functional import cached_property
from fuse import FuseOSError, Operations
# from fuse import LoggingMixIn
import audiotools

from musicdb import models


class MusicFsEntry(Operations):
    instance = None
    fd = {}
    last_fd = 0

    @classmethod
    def from_fd(cls, fd):
        return MusicFsEntry.fd[fd]

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

    def set_fd(self):
        MusicFsEntry.last_fd += 1
        MusicFsEntry.fd[MusicFsEntry.last_fd] = self
        return MusicFsEntry.last_fd

    @staticmethod
    def get_by_fd(fd_id):
        return MusicFsEntry.fd[fd_id]

    @staticmethod
    def clean_fd(fd):
        MusicFsEntry.fd.pop(fd)


class MusicDir(MusicFsEntry):
    inode = 0

    @classmethod
    def from_path(cls, path):
        obj = None
        if len(path) == 0:
            obj = cls()
        elif len(path) == 1:
            album_id = cache.get('fuse-%s-%s-pk' % (cls.__name__, hashlib.md5(path[0].encode('utf-8')).hexdigest()))
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
            path = self.MusicDir.fat_restrict(u"%s–%d–%s" % (album.artist.name, album.date.year, album.title))
            cache.set('fuse-%s-%s-pk' % (
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
        cache_key = 'fuse-%s-%s-list' % (
                self.__class__.__name__, hashlib.md5(self.path().encode('utf-8')).hexdigest())
        result = ['.', '..']
        if cache.get(cache_key):
            result += cache.get(cache_key)
        else:
            entries = self.entries()
            cache.set(cache_key, entries.keys())
            result += entries.keys()
        return result

    def opendir(self, *args):
        return self.set_fd()

    def getattr(self, *args):
        attrs = dict({
            'st_ino': self.inode,
            'st_mode': stat.S_IFDIR | 0555,  # mode
            'st_nlink': 1,      # nlink
            'st_uid':  0,       # uid
            'st_gid':  0,       # gid
            'st_size': 1,       # size
            'st_atime': random.randint(1, 3600)*86400,      # int(rand(3600))*86400, #atime
            'st_mtime': 0,      # int(rand(3600))*86400, #mtime
            'st_ctime': 0,       # int(rand(3600))*86400, #ctime
        })
        if self.instance:
            attrs['st_ctime'] = calendar.timegm(self.instance.add_time.timetuple())
        return attrs


class MusicFile(MusicFsEntry):
    instance = None
    fh = None
    rwlock = Lock()

    @classmethod
    def from_path(cls, path):
        if len(path) != 2:
            raise FuseOSError(ENOENT)
        dir = MusicDir.from_path((path[0],))
        files = dir.entries()
        return files[path[1]]

    def __init__(self, instance):
        self.instance = instance

    @cached_property
    def audiotools_audiofile(self):
        audiotools_filename = audiotools.Filename.from_unicode(self.abs_path())
        audiofile = audiotools.open_files((audiotools_filename,))[0]
        return audiofile

    def get_metadata(self):
        audiofile = self.audiotools_audiofile
        return audiofile.get_metadata()

    @cached_property
    def currentmeta(self):
        meta = self.get_metadata()
        return meta

    @cached_property
    def newmeta(self):
        meta = self.get_metadata()

        track = self.instance
        newmeta = audiotools.MetaData(
                track_name=track.title,
                track_number=track.track_num,
                album_name=track.album.title,
                artist_name=track.album.artist.name,
                year=track.album.date.year,
        )
        if track.track_artist:
            newmeta.artist_name = track.track_artist
        new_vorbismeta = audiotools.VorbisComment.converted(newmeta)
        new_vorbismeta[u'ALBUMARTIST'] = [track.album.artist.name]

        new_vorbismeta[u'REPLAYGAIN_REFERENCE_LOUDNESS'] = [u'89.0 dB']
        new_vorbismeta[u'REPLAYGAIN_ALBUM_GAIN'] = [unicode(track.album.rg_gain) + u' dB']
        new_vorbismeta[u'REPLAYGAIN_ALBUM_PEAK'] = [unicode(track.album.rg_peak)]
        new_vorbismeta[u'REPLAYGAIN_TRACK_GAIN'] = [unicode(track.rg_gain) + u' dB']
        new_vorbismeta[u'REPLAYGAIN_TRACK_PEAK'] = [unicode(track.rg_peak)]

        new_vorbismeta[u'MUSICBRAINZ_TRACKID'] = [u'MY_'+unicode(track.pk)]

        new_vorbiscomment = audiotools.flac.Flac_VORBISCOMMENT.converted(new_vorbismeta)

        if meta.has_block(new_vorbiscomment.BLOCK_ID):
            meta.replace_blocks(new_vorbiscomment.BLOCK_ID, [new_vorbiscomment])
        else:
            meta.add_block(new_vorbiscomment)
        return meta

    @staticmethod
    def metatobytes(meta):
        meta_bytes = StringIO.StringIO()
        writer = audiotools.bitstream.BitstreamWriter(meta_bytes, False)
        writer.write_bytes("fLaC")

        meta.build(writer)

        return meta_bytes

    @cached_property
    def currentheader_bytes(self):
        return self.__class__.metatobytes(self.currentmeta)

    @cached_property
    def newheader_bytes(self):
        return self.__class__.metatobytes(self.newmeta)

    @cached_property
    def size_diff(self):
        return self.newheader_bytes.len - self.currentheader_bytes.len

    def getattr(self, *args):
        statinfo = os.stat(self.abs_path())
        return dict({
            'st_ino': self.instance.pk,      # ino
            'st_mode': stat.S_IFREG | 0444,  # mode
            'st_nlink': 1,      # nlink
            'st_uid':  0,       # uid
            'st_gid':  0,       # gid
            'st_size': statinfo.st_size + self.size_diff,       # size
            'st_atime': 0,      # int(rand(3600))*86400, #atime
            'st_mtime': 0,      # int(rand(3600))*86400, #mtime
            'st_ctime': 0,       # int(rand(3600))*86400, #ctime
        })

    def path(self):
        track = self.instance
        return self.__class__.fat_restrict(u"%02d–%s.flac" % (track.track_num, track.title))

    def abs_path(self):
        return os.path.join(settings.MUSIC_LIBRARY_PATH, self.instance.album.path, self.instance.path)

    def open(self, *args):
        self.fh = io.open(self.abs_path(), "rb")
        return self.set_fd()

    def read(self, path, size, offset, fh, recursion=False):
        if not recursion:
            self.rwlock.acquire()
        try:
            if offset < self.newheader_bytes.len:
                self.newheader_bytes.seek(offset, 0)
                result = self.newheader_bytes.read(size)

                if len(result) < size:
                    result += self.read(path, size - len(result), offset + len(result), fh, True)
            else:
                self.fh.seek(offset - self.size_diff, 0)
                result = self.fh.read(size)
        finally:
            if not recursion:
                self.rwlock.release()
        return result


class Loopback(Operations):
    def __call__(self, op, *args, **kwargs):
        if op == 'init':
            return self.__init__()
        else:
            path = args[0]

            fd = None
            instance = None
            if op in ('flush', 'fsync', 'fsyncdir', 'getattr', 'read', 'readdir', 'truncate', 'write', 'release',
                      'releasedir', 'release', 'releasedir'):
                fd = args[-1]
                if fd:
                    instance = MusicFsEntry.get_by_fd(fd)

            # clean fd list
            if op in ('release', 'releasedir'):
                fd = args[1]
                MusicFsEntry.clean_fd(fd)

            if not instance:
                path_list = filter(lambda x: x != '', path.split('/'))
                if len(path_list) < 2:
                    instance = MusicDir.from_path(path_list)
                else:
                    instance = MusicFile.from_path(path_list)

            result = instance.__call__(op, *args)
            return result
