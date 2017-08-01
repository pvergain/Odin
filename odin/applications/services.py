from datetime import date

from .models import (
    Application,
    ApplicationInfo,
    IncludedApplicationTask,
    ApplicationTask,
    ApplicationSolution
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
    return instance


def create_included_application_task(*,
                                     name: str=None,
                                     description: str=None,
                                     gradable: bool=False,
                                     existing_task: ApplicationTask=None,
                                     application_info: ApplicationInfo=None) -> IncludedApplicationTask:

    included_task = IncludedApplicationTask(application_info=application_info)
    if existing_task is None:
        existing_task = ApplicationTask(name=name, description=description, gradable=gradable)
        existing_task.full_clean()
        existing_task.save()

    included_task.name = existing_task.name
    included_task.description = existing_task.description
    included_task.gradable = existing_task.gradable

    included_task.task = existing_task
    included_task.full_clean()
    included_task.save()

    return included_task


def create_application_solution(*,
                                task: IncludedApplicationTask,
                                application: Application,
                                url: str) -> ApplicationSolution:
    solution_qs = ApplicationSolution.objects.filter(task=task, application=application)

    if solution_qs.exists():
        solution = solution_qs.first()
        solution.url = url
        solution.save()
    else:
        solution = ApplicationSolution.objects.create(task=task, application=application, url=url)

    return solution
