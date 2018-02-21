from datetime import date

from django.apps import apps

from .models import (
    Application,
    ApplicationInfo,
)
from odin.education.models import Course
from odin.users.models import BaseUser


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
                       full_name: str,
                       phone: str=None,
                       skype: str=None,
                       works_at: str=None,
                       studies_at: str=None,
                       has_interview_date: bool=False) -> Application:

    instance = Application(
        application_info=application_info,
        user=user,
        phone=phone,
        skype=skype,
        works_at=works_at,
        studies_at=studies_at,
        has_interview_date=has_interview_date
    )

    instance.full_clean()
    instance.save()

    if user.profile:
        user.profile.full_name = full_name
        user.profile.save()

    if application_info.has_competition:
        application_info.competition.participants.add(user)

    return instance


def get_last_solutions_for_application(*, application: Application):
    Solution = apps.get_model('competitions', 'Solution')

    tasks = {
        task: Solution.objects.filter(
            participant=application.user,
            task=task
        ).last()
        for task in application.application_info.competition.tasks.all()
    }

    return tasks


def get_partially_completed_applications(*, application_info: ApplicationInfo):
    related = ['interview_person']

    applications = Application.objects.select_related(*related).filter(application_info=application_info)
    result = []

    for application in applications:
        if application.is_partially_completed:
            result.append(application)

    return result
