import logging

from django.conf import settings
from django.core.mail import send_mail as django_send_mail

from .utils import serialize_context, filter_kwargs
from .tasks import (
    send_mail as celery_send_mail,
    send_template_mail as celery_send_template_mail
)


logger = logging.getLogger(__name__)


def send_mail(**kwargs):
    """
    This is the entry point for all email sending.
    This function decides how to send the email.
    Possible options are:
    * Mandrill using a specified template.
    * Mandrill without template (needs subject + body)
    * Using Django's email system defined by EMAIL_BACKEND
    """
    if not settings.SEND_MAIL_TO_USERS:
        logger.warning('Email sending triggered, but no email is going to be sent.')
        return

    template_name = kwargs.get('template_name')

    if template_name is not None and template_name in settings.SKIP_SENDING_ON_TEMPLATES:
        logger.warning(f'{template_name} is disabled by SKIP_SENDING_ON_TEMPLATES.')
        return

    if settings.USE_DJANGO_SEND_MAIL:
        f = _send_django_mail
    elif 'template_name' in kwargs:
        f = _send_template_mail
    else:
        f = _send_standard_mail

    args = filter_kwargs(f, **kwargs)
    return f(**args)


def _send_standard_mail(*,
                        subject,
                        recipients,
                        body,
                        context=None,
                        from_mail=None):

    context = serialize_context(context)

    if from_mail is None:
        from_mail = settings.DEFAULT_FROM_EMAIL

    result = celery_send_mail.delay(subject=subject,
                                    recipients=recipients,
                                    body=body,
                                    context=context,
                                    from_mail=from_mail)

    return result


def _send_template_mail(*,
                        template_name,
                        recipients,
                        context=None,
                        from_mail=None):

    context = serialize_context(context)

    if from_mail is None:
        from_mail = settings.DEFAULT_FROM_EMAIL

    result = celery_send_template_mail.delay(template_name=template_name,
                                             recipients=recipients,
                                             context=context,
                                             from_mail=from_mail)

    return result


def _send_django_mail(*,
                      subject=None,
                      recipients,
                      body=None,
                      from_mail=None):
    if subject is None:
        subject = 'Subject was not provided. Possibly sending a template email.'

    if body is None:
        body = 'Body was not provided, Possible sending a template email.'

    if from_mail is None:
        from_mail = settings.DEFAULT_FROM_EMAIL

    django_send_mail(subject, body, from_mail, recipients)
