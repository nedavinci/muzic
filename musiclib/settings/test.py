import os

from defaults import *
DEBUG = True

FORCE_SCRIPT_NAME = '/musiclib'
MUSIC_LIBRARY_PATH = '/home/music/lossless/'

STATIC_URL = FORCE_SCRIPT_NAME + '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")
