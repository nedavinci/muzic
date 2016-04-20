import os

from defaults import *
DEBUG = True

SECRET_KEY = '8k4ts_@ywt_jf1i!xuvo$1&14yk(skj-35c^v$b7_fxrfai(-p'

MUSIC_LIBRARY_PATH = '/mnt/lossless/'

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
