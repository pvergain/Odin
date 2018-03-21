from __future__ import absolute_import

import mandrill

from celery import shared_task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

from django.conf import settings

from .utils import get_mandrill_api_key, build_message


logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=settings.CELERY_TASK_MAX_RETRIES)
def send_mail(self, subject, recipients, body, from_mail, context, **kwargs):
    api_key = get_mandrill_api_key()
    client = mandrill.Mandrill(api_key)

    message = build_message(recipients, context)
    message['from_email'] = from_mail
    message['subject'] = subject
    message['html'] = body
    message['text'] = body

    try:
        result = client.messages.send(message=message)
        return result
    except SoftTimeLimitExceeded as e:
        logger.exception('Soft time limit exceeded when sending email')
        self.retry(exc=e)
    except mandrill.Error as e:
        logger.exception('A mandrill error occurred: %s - %s' % (e.__class__, e))
        self.retry(exc=e)


@shared_task(bind=True, max_retries=settings.CELERY_TASK_MAX_RETRIES)
def send_template_mail(self, template_name, recipients, context, **kwargs):
    api_key = get_mandrill_api_key()
    client = mandrill.Mandrill(api_key)

    message = build_message(recipients, context)

    try:
        result = client.messages.send_template(template_name, [], message)
        return result
    except SoftTimeLimitExceeded as e:
        logger.exception('Soft time limit exceeded when sending email')
        self.retry(exc=e)
    except mandrill.Error as e:
        logger.exception('A mandrill error occurred: %s - %s' % (e.__class__, e))
        self.retry(exc=e)
