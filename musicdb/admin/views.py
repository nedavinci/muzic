from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView

import audiotools
from musicdb.models import Album

from .forms import AlbumFromPathForm


class AlbumFromPathView(FormView):
    template_name = 'album_path.html'
    form_class = AlbumFromPathForm

    def form_valid(self, form):
        return redirect('admin:musicdb_album_change', form.cleaned_data['path'])


class AlbumRecalculateRGView(RedirectView):
    permanent = False
    query_string = False
    pattern_name = 'admin:musicdb_album_change'

    def get_redirect_url(self, *args, **kwargs):
        album = get_object_or_404(Album, pk=kwargs['pk'])
        filenames = []
        album_tracks = album.track_set.all()
        for track in album_tracks:
            filenames.append(audiotools.Filename.from_unicode(track.get_fullpath()))
        at_files = audiotools.open_files(filenames, False)
        rg_list = audiotools.calculate_replay_gain(at_files)
        for index, rg in enumerate(rg_list):
            track = album_tracks[index]
            track.rg_gain = rg[1]
            track.rg_peak = rg[2]
            track.save()
            if index == 0:
                album.rg_gain = rg[3]
                album.rg_peak = rg[4]
                album.save()
        return super(AlbumRecalculateRGView, self).get_redirect_url(kwargs['pk'])
