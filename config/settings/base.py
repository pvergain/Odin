from django.urls import reverse_lazy
from django.apps import apps
import environ

ROOT_DIR = environ.Path(__file__) - 3  # (odin/config/settings/base.py - 3 = odin/)
APPS_DIR = ROOT_DIR.path('odin')

env = environ.Env()

DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'collectfast',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.postgres'
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'crispy_forms',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'captcha',
    'widget_tweaks',
    'django_filters',
    'easy_thumbnails',
    'django_js_reverse',
]

LOCAL_APPS = [
    'odin.common.apps.CommonConfig',
    'odin.dashboard.apps.DashboardConfig',
    'odin.authentication.apps.AuthenticationConfig',
    'odin.users.apps.UsersConfig',
    'odin.education.apps.EducationConfig',
    'odin.management.apps.ManagementConfig',
    'odin.grading.apps.GradingConfig',
    'odin.applications.apps.ApplicationsConfig',
    'odin.interviews.apps.InterviewsConfig',
    'odin.competitions.apps.CompetitionsConfig'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIGRATION_MODULES = {
    'sites': 'odin.contrib.sites.migrations'
}

DEBUG = env.bool('DJANGO_DEBUG', False)


ADMINS = [
    ("""HackSoft""", 'radorado@hacksoft.io'),
]

MANAGERS = ADMINS

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///odin'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en-us'


SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

from .allauth import *
from .captcha import *

STATIC_ROOT = str(ROOT_DIR('staticfiles'))

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    str(ROOT_DIR.path('ui/images')),
    str(ROOT_DIR.path('ui/bower_components')),
    str(ROOT_DIR.path('ui/assets')),
    str(ROOT_DIR.path('dist')),
]


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_ROOT = str(ROOT_DIR('media'))

MEDIA_URL = '/media/'

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


AUTH_USER_MODEL = 'users.BaseUser'

AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

ADMIN_URL = r'^admin/'

# Github OAuth settings
GH_OAUTH_CLIENT_ID = env('GH_OAUTH_CLIENT_ID', default='')
GH_OAUTH_SECRET_KEY = env('GH_OAUTH_SECRET_KEY', default='')


# Celery settings
CELERY_BROKER_URL = env('BROKER_URL', default='amqp://guest:guest@localhost//')
CELERY_BROKER_POOL_LIMIT = 1
CELERY_BROKER_HEARTBEAT = None
CELERY_BROKER_CONNECTION_TIMEOUT = 30

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_TASK_SOFT_TIME_LIMIT = env('CELERY_TASK_SOFT_TIME_LIMIT', default=60)
CELERY_TASK_TIME_LIMIT = env('CELERY_TASK_TIME_LIMIT', default=60+60)
CELERY_TASK_MAX_RETRIES = env('CELERY_TASK_MAX_RERIES', default=3)

# Mandrill settings
USE_DJANGO_EMAIL_BACKEND = True

MANDRILL_API_KEY = env('MANDRILL_API_KEY', default='')

templates = {
    'account_email_email_confirmation_signup': lambda **env_kwargs: env('MANDRILL_SIGNUP_CONFIRM', **env_kwargs),
    'account_email_email_confirmation': lambda **env_kwargs: env('MANDRILL_CONFIRMATION', **env_kwargs),
    'account_email_password_reset_key': lambda **env_kwargs: env('MANDRILL_PASSWORD_RESET', **env_kwargs),
    'account_email_email_competition_confirmation': lambda **env_kwargs: env('MANDRILL_COMPETITION_CONFIRMATION', **env_kwargs),
    'application_completed_default': lambda **env_kwargs: env('MANDRILL_APPLICATION_COMPLETED', **env_kwargs),
    'interview_confirmation': lambda **env_kwargs: env('MANDRILL_INTERVIEW_CONFIRMATION', **env_kwargs),
    'course_information_email': lambda **env_kwargs: env('MANDRILL_COURSE_INFORMATION', **env_kwargs)
}

EMAIL_TEMPLATES = {
    key: f(default='')
    for key, f in templates.items()
}

TASK_PASSED = "Passed"
TASK_FAILED = "Failed"
TASK_NOT_SENT = "Not sent"

from .grader import *
