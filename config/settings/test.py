from .local import *  # noqa

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

TEMPLATES[0]['OPTIONS']['loaders'] = [
    ['django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ], ],
]

BROKER_BACKEND = 'memory'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

USE_DJANGO_EMAIL_BACKEND = True

COVERALLS_REPO_TOKEN = env('COVERALLS_REPO_TOKEN', default='')
