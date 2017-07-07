from django.conf import settings
from django.core.mail import send_mail as django_send_mail

from .tasks import send_template_mail


def send_email(template_name, recipients, context, **kwargs):
    if settings.USE_DJANGO_EMAIL_BACKEND:
        django_send_mail(kwargs.get('subject'), str(context), kwargs.get('from_mail'), recipients)
    else:
        send_template_mail.delay(template_name, recipients, context, **kwargs)
