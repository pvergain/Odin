from celery import shared_task

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse

from odin.common.services import send_email
from odin.applications.models import ApplicationInfo
from odin.education.services import add_student
from odin.education.models import Student

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


@shared_task(bind=True)
def promote_accepted_users_to_students(self):
    active_application_infos = ApplicationInfo.objects.get_open_for_interview()
    for info in active_application_infos:
        accepted = info.accepted_applicants
        for application in accepted:
            if not application.user.is_student():
                student = Student.objects.create_from_user(application.user)
            else:
                student = application.user.student

            add_student(course=info.course, student=student)
