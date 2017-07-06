from __future__ import absolute_import, unicode_literals
from celery import shared_task
import mandrill

from django.conf import settings

from .utils import build_message


@shared_task(bind=True)
def send_template_mail(self, template_name, recipients, context, **kwargs):
    api_key = settings.MANDRILL_API_KEY
    client = mandrill.Mandrill(api_key)

    message = build_message(recipients, context)

    result = client.messages.send_template(template_name=template_name, template_content=[], message=message)
    return result
