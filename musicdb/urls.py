from django.conf.urls import include, url
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    url(r'^select2/', include('django_select2.urls')),
]

if settings.DEBUG:
    urlpatterns.append(
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MUSIC_LIBRARY_PATH},)
    )
