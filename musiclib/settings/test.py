import os

from defaults import *
DEBUG = True

FORCE_SCRIPT_NAME = '/musiclib'
MUSIC_LIBRARY_PATH = '/home/music/lossless/'

MUSIC_LIBRARY_BASE_URL = FORCE_SCRIPT_NAME + MUSIC_LIBRARY_BASE_URL
STATIC_URL = FORCE_SCRIPT_NAME + '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")

INSTALLED_APPS.extend(('debug_toolbar', 'django_extensions', 'template_timings_panel'))
INTERNAL_IPS = ('192.168.154.60',)
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]
