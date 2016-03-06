from django.conf.urls import url
from .views import HandShake, NowPlaying, Submission

urlpatterns = [
    url(r'^handshake/$', HandShake.as_view(), name='handshake'),
    url(r'^now_playing/$', NowPlaying.as_view(), name='now_playing'),
    url(r'^submission/$', Submission.as_view(), name='submission'),
]
