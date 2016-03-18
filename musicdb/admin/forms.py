from django import forms
from django.conf import settings

from .fields import AlbumPathField
from ..models import Album


class AlbumFromPathForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(AlbumFromPathForm, self).__init__(*args, **kwargs)
        paths_in_db = Album.objects.exclude(path__isnull=True).values_list('path', flat=True)
        self.fields['path'] = AlbumPathField(
                path=unicode(settings.MUSIC_LIBRARY_PATH),
                recursive=True,
                allow_files=False,
                allow_folders=True,
                exclude_dirs=paths_in_db)

    # class Media:
    #     js = ('admin/js/vendor/jquery/jquery.js', 'admin/js/jquery.init.js')
