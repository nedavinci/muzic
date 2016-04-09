import os

from defaults import *
DEBUG = True

MUSIC_LIBRARY_PATH = '/mnt/lossless/'

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")

INSTALLED_APPS.extend(('debug_toolbar', 'django_extensions', 'cacheops'))

CACHEOPS_REDIS = {
    'host': 'localhost', # redis-server is on same machine
    'port': 6379,        # default redis port
    'db': 1,             # SELECT non-default redis database
                         # using separate redis db or redis instance
                         # is highly recommended

    'socket_timeout': 3,   # connection timeout in seconds, optional
}

# Alternatively the redis connection can be defined using a URL:
# CACHEOPS_REDIS = "redis://localhost:6379/1"

CACHEOPS = {
    '*.*': {'ops': 'all', 'timeout': 60*60},
}
