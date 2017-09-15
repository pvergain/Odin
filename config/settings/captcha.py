import environ

env = environ.Env()

NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default='')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_SECRET_KEY', default='')
RECAPTCHA_USE_SSL = True
