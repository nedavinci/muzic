import os

from defaults import *
DEBUG = True

MUSIC_LIBRARY_PATH = '/mnt/lossless/'

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")

INSTALLED_APPS.extend(('debug_toolbar', 'django_extensions'))
