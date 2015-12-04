from django.conf.urls import url
from django.conf import settings

urlpatterns = [
]

if settings.DEBUG:
    urlpatterns.append(
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MUSIC_LIBRARY_PATH},
            name="music-library-static")
    )
