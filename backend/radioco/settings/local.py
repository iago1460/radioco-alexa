from radioco.settings import *

# import ptvsd
# ptvsd.enable_attach(None, address=('0.0.0.0', 3000))

INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]


MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
SHOW_TOOLBAR_CALLBACK = lambda request: True
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'radioco.settings.local.SHOW_TOOLBAR_CALLBACK'
}

NOTEBOOK_ARGUMENTS = [
    '--allow-root',
    '--ip', '0.0.0.0',
    '--port', '8888',
]

LOGLEVEL = 'DEBUG'
