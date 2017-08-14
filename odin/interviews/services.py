from datetime import date, time

from django.core.exceptions import ValidationError

from odin.applications.models import Application
from .models import Interview, Interviewer, InterviewerFreeTime


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
                                 buffer_time: bool) -> InterviewerFreeTime:

    return InterviewerFreeTime.objects.create(interviewer=interviewer,
                                              date=date,
                                              start_time=start_time,
                                              end_time=end_time,
                                              buffer_time=buffer_time)
