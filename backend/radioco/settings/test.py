import os
from radioco.settings import *

DEBUG = False

# Disable sentry during testing
os.environ.pop('SENTRY_DSN', None)

# Ensure exceptions etc are output to console during tests
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        }
    },
}
