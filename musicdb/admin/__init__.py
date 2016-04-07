from django.contrib import admin

from .. import models
from .album import AlbumAdmin


class PlayLogAdmin(admin.ModelAdmin):
        date_hierarchy = 'time'
        list_display = ('time', 'source', 'track')
        readonly_fields = ('time', 'source', 'track')
        search_fields = ['track__title', 'track__album__title',
                         'track__album__artist__name']
        list_filter = (
            'source',
            'track__album'
        )


class TrackAdmin(admin.ModelAdmin):
        search_fields = 'title',
        readonly_fields = 'path',


admin.site.register(models.Artist)
admin.site.register(models.Album, AlbumAdmin)
admin.site.register(models.Track, TrackAdmin)
admin.site.register(models.Label)
admin.site.register(models.Genre)
admin.site.register(models.PlayLog, PlayLogAdmin)
