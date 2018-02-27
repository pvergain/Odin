from datetime import date

from django.apps import apps

from .models import (
    Application,
    ApplicationInfo,
)
from odin.education.models import Course
from odin.users.models import BaseUser

from odin.competitions.models import Solution


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


def add_interview_person_to_application(*, application: Application, interview_person: BaseUser) -> Application:
    application.interviewer_person = interview_person
    application.save()

    return application


def generate_last_solutions_per_participant() -> 'last_solutions_per_task_per_participant_DICT':
    '''
    raw_solutions structure

    raw_solutions[solution] = [(participant_id, task_id, solution_id), ...]
    '''

    raw_solutions = Solution.objects.values_list(
        'participant', 'task', 'id').order_by('participant', 'task', '-id')
    solutions = {}

    for solution in raw_solutions:
        if solution[0] in solutions.keys():
            if solution[1] in solutions[solution[0]].keys():
                pass
            else:
                solutions[solution[0]].update({solution[1]: solution[2]})
        else:
            solutions[solution[0]] = {solution[1]: solution[2]}

    return solutions


def get_valid_solutions(*, application_info: ApplicationInfo,
                        solutions: 'last_solutions_per_task_per_participant_DICT') -> 'valid_solutions_DICT':
    '''
    solutions structure
        solutions[solution] = (participant_id, task_id, solution_id)

    '''
    tasks_count = application_info.competition.tasks.all().count()

    valid_solutions = {}

    for item in solutions.keys():
        if len(solutions[item].keys()) == tasks_count:
            valid_solutions.update({item: solutions[item]})
    else:
        pass

    return valid_solutions


def get_partially_completed_applications(*, valid_solutions: 'valid_solutions_DICT',
                                         application_info: ApplicationInfo):
    '''
    expected valid_solutions structure

    valid_solutions = {user_id: {task_idX: solution_id, task_idX+1:solution_id, task_idX+n: solution_id}, ...}
    '''
    valid_solutions_criteria = [user_id for user_id in valid_solutions.keys()]

    applications = []
    all_applications = application_info.applications.all().select_related('user', 'interview_person')

    for application in all_applications:
        if application.user.id in valid_solutions_criteria:
            applications.append(application)
        else:
            pass

    return applications
