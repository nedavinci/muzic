from .forms import AlbumFromPathForm
from django.views.generic.edit import FormView
from django.shortcuts import redirect


class AlbumFromPathView(FormView):
    template_name = 'album_path.html'
    form_class = AlbumFromPathForm

    def form_valid(self, form):
        return redirect('admin:musicdb_album_change', form.cleaned_data['path'])
