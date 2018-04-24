from .base import *  # noqa
from .aws import *

DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

SECRET_KEY = env('DJANGO_SECRET_KEY', default=':xr@79Ca47cL/L]qcuptu$}=.<`J=U4lr1kom3o`HcjO{*j@{k')

EMAIL_PORT = 1025

EMAIL_HOST = 'localhost'
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
                    default='django.core.mail.backends.console.EmailBackend')


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', ]

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

INSTALLED_APPS += ['django_extensions', ]

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

MEDIA_LOCATION = 'media'
MEDIA_URL = 'https://%s/%s/%s/' % (AWS_S3_HOST, AWS_STORAGE_BUCKET_NAME, MEDIA_LOCATION)
MEDIA_S3_CUSTOM_DOMAIN = '%s/%s' % (AWS_S3_HOST, AWS_STORAGE_BUCKET_NAME)

DEFAULT_FILE_STORAGE = 'config.settings.storages.MediaStorage'

STATIC_LOCATION = 'static'
STATIC_URL = 'https://%s/%s/%s/' % (AWS_S3_HOST, AWS_STORAGE_BUCKET_NAME, STATIC_LOCATION)
STATIC_CDN_CUSTOM_DOMAIN = '%s/%s' % (AWS_S3_HOST, AWS_STORAGE_BUCKET_NAME)

STATICFILES_STORAGE = 'config.settings.storages.StaticStorage'
