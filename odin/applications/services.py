from datetime import date

from django.conf import settings

from .models import (
    Application,
    ApplicationInfo,
)
from odin.education.models import Course
from odin.users.models import BaseUser
from odin.common.services import send_email
from odin.competitions.models import CompetitionParticipant


def create_application_info(*,
                            start_date: date,
                            end_date: date,
                            course: Course,
                            start_interview_date: date=None,
                            end_interview_date: date=None,
                            description: str=None,
                            external_application_form: str=None) -> ApplicationInfo:

    instance = ApplicationInfo(start_date=start_date,
                               end_date=end_date,
                               course=course,
                               start_interview_date=start_interview_date,
                               end_interview_date=end_interview_date,
                               description=description,
                               external_application_form=external_application_form)

    instance.full_clean()
    instance.save()

    return instance


def create_application(*,
                       application_info: ApplicationInfo,
                       user: BaseUser,
                       phone: str=None,
                       skype: str=None,
                       works_at: str=None,
                       studies_at: str=None,
                       has_interview_date: bool=False) -> Application:

    instance = Application(application_info=application_info,
                           user=user,
                           phone=phone,
                           skype=skype,
                           works_at=works_at,
                           studies_at=studies_at,
                           has_interview_date=has_interview_date)

    instance.full_clean()
    instance.save()

    if application_info.competition:
        if not hasattr(user, 'competitionparticipant'):
            participant = CompetitionParticipant.objects.create_from_user(user)
        application_info.competition.participants.add(participant)

    template_name = settings.EMAIL_TEMPLATES.get('application_completed_default')
    context = {
        'user': user.email,
        'course': application_info.course.name
    }
    send_email(template_name=template_name, recipients=[user.email], context=context)

    return instance
