from django.urls import reverse_lazy
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
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.postgres'
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'captcha',
    'widget_tweaks',
    'django_filters'
]

LOCAL_APPS = [
    'odin.dashboard.apps.DashboardConfig',
    'odin.authentication.apps.AuthenticationConfig',
    'odin.users.apps.UsersConfig',
    'odin.education.apps.EducationConfig',
    'odin.management.apps.ManagementConfig',
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


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

LOGIN_URL = reverse_lazy('account_login')
LOGIN_REDIRECT_URL = reverse_lazy('dashboard:users:profile')
ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy('account_login')
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
SOCIALACCOUNT_ADAPTER = "odin.authentication.adapter.CustomAdapter"
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': [
            'user:email',
        ],
    }
}


# Recaptcha settings
NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default='')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_SECRET_KEY', default='')
RECAPTCHA_USE_SSL = True

STATIC_ROOT = str(ROOT_DIR('staticfiles'))

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    str(ROOT_DIR.path('ui/images')),
    str(ROOT_DIR.path('ui/bower_components')),
    str(ROOT_DIR.path('ui/assets')),
]


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_ROOT = str(APPS_DIR('media'))

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
