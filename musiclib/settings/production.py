from defaults import *
DEBUG = False

FORCE_SCRIPT_NAME = '/musiclib'
MUSIC_LIBRARY_PATH = '/home/music/lossless/'

MUSIC_LIBRARY_BASE_URL = FORCE_SCRIPT_NAME + MUSIC_LIBRARY_BASE_URL
STATIC_URL = FORCE_SCRIPT_NAME + '/static/'
ALLOWED_HOSTS = ["*"]

# INSTALLED_APPS.extend(('cacheops',))
# 
# CACHEOPS_REDIS = {
#     'host': 'localhost',
#     'port': 6379,       
#     'db': 1,            
#     'socket_timeout': 3,
# }
# 
# CACHEOPS = {
#     'musiclib.*': {'ops': 'all', 'timeout': 60*60},
# }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/nnm/projects/musiclib/run/django.errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
