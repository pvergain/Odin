from datetime import date, time

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from odin.common.services import send_email
from odin.applications.models import Application, ApplicationInfo
from odin.education.models import Course
from .models import Interview, Interviewer, InterviewerFreeTime
from .helpers.interviews import GenerateInterviews, GenerateInterviewSlots


def create_new_interview_for_application(*,
                                         application: Application,
                                         uuid: str) -> Interview:
    new_interview = Interview.objects.filter(uuid=uuid).first()

    if new_interview.application is not None:
        raise ValidationError("This interview is already taken!")

    old_interview = Interview.objects.filter(application=application).first()
    old_interview.reset()

    new_interview.application = application
    new_interview.has_received_email = True
    new_interview.has_confirmed = True
    new_interview.save()

    return new_interview


def create_interviewer_free_time(*,
                                 interviewer: Interviewer,
                                 date: date,
                                 start_time: time,
                                 end_time: time,
                                 interview_time_length: int,
                                 break_time: int) -> InterviewerFreeTime:

    return InterviewerFreeTime.objects.create(interviewer=interviewer,
                                              date=date,
                                              start_time=start_time,
                                              end_time=end_time,
                                              interview_time_length=interview_time_length,
                                              break_time=break_time)


def add_course_to_interviewer_courses(*,
                                      interviewer: Interviewer,
                                      course: Course) -> QuerySet:
    if not hasattr(course, 'application_info'):
        raise ValidationError('Applications for this course are closed')
    interviewer.courses_to_interview.add(course.application_info)
    return interviewer.courses_to_interview.all()


def generate_interview_slots():
    context = {'log': []}
    context['log'].append("Start generating interviews...\n")

    interview_slots_generator = GenerateInterviewSlots()

    interview_slots_generator.generate_interview_slots()
    interview_slots_generator.get_generated_slots()

    courses_to_interview = ApplicationInfo.objects.get_open_for_interview()

    if len(courses_to_interview) == 0:
        context['log'].append('There are no open for interview courses!\n')
        context['log'].append('No interviews will be generated.')

    for info in courses_to_interview:
        context['log'].append("Generate interviews for {0}".format(info.course.name))
        interview_generator = GenerateInterviews(application_info=info)
        app_without_interviews = interview_generator.get_applications_without_interviews()
        free_interview_slots = interview_generator.get_free_interview_slots()
        if app_without_interviews > free_interview_slots:
            context['log'].append("Not enough free slots - {0}".format(app_without_interviews - free_interview_slots))
            continue

        interview_generator.generate_interviews()

        free_interview_slots = interview_generator.get_free_interview_slots()
        context['log'].append('Generated interviews: {0}'.format(
            interview_generator.get_generated_interviews_count()))
        context['log'].append('Applications without interviews: {0} '.format(
            interview_generator.get_applications_without_interviews()))
        context['log'].append('All free interview slots: {0}'.format(free_interview_slots))

    return context


def send_interview_confirmation_emails():
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
