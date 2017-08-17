from celery import shared_task

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse

from odin.common.services import send_email

from .models import Interview


@shared_task(bind=True)
def send_interview_confirmation_emails(self):
    interviews = Interview.objects.with_application().without_received_email()
    for interview in interviews:
        application = interview.application
        user = application.user
        confirm_url_kwargs = {"application_id": application.id,
                              "interview_token": str(interview.uuid)}
        context = {
            'protocol': 'http',
            'full_name': user.get_full_name(),
            'course_name': application.application_info.course.name,
            'start_time': str(interview.start_time),
            'date': str(interview.date),
            'domain': Site.objects.get_current().domain,
            'confirm_url': reverse('dashboard:interviews:confirm-interview',
                                   kwargs=confirm_url_kwargs),
            'choose_url': reverse('dashboard:interviews:choose-interview',
                                  kwargs={"application_id": application.id,
                                          "interview_token": str(interview.uuid)})

        }

        print('Sending to {} for application {}'.format(user.email, application))

        email_template = settings.EMAIL_TEMPLATES['interview_confirmation']
        send_email(email_template, [user.email], context)

        interview.has_received_email = True
        interview.save()
