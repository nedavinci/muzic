import os

from defaults import *
DEBUG = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
MUSIC_LIBRARY_PATH = os.path.join(os.path.expanduser("~"), "musiclibtest")

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")
