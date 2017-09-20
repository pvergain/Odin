import environ

env = environ.Env()

SENTRY_DSN = env('DJANGO_SENTRY_DSN', default='')

if bool(SENTRY_DSN):
    SENTRY_CLIENT = env('DJANGO_SENTRY_CLIENT', default='raven.contrib.django.raven_compat.DjangoClient')
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry', ],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console', ],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console', ],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console', ],
                'propagate': False,
            },
            'django.security.DisallowedHost': {
                'level': 'ERROR',
                'handlers': ['console', 'sentry', ],
                'propagate': False,
            },
        },
    }
    SENTRY_CELERY_LOGLEVEL = env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO)
    RAVEN_CONFIG = {
        'CELERY_LOGLEVEL': env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO),
        'DSN': SENTRY_DSN
    }
