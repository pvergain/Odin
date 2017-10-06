import uuid
from typing import BinaryIO, Dict, Tuple

from django.core.exceptions import ValidationError

from odin.education.models import Material, Task, Test, ProgrammingLanguage
from odin.users.models import BaseUser
from odin.users.services import create_user

from .models import CompetitionMaterial, Competition, CompetitionTask, CompetitionParticipant, Solution, CompetitionTest


def create_competition_material(*,
                                identifier: str=None,
                                url: str=None,
                                content: str=None,
                                competition: Competition=None,
                                existing_material: Material=None) -> CompetitionMaterial:
    competition_material = CompetitionMaterial(competition=competition)

    if existing_material is None:
        existing_material = Material(identifier=identifier, url=url, content=content)
        existing_material.full_clean()
        existing_material.save()

    competition_material.identifier = existing_material.identifier
    competition_material.content = existing_material.content

    competition_material.material = existing_material
    competition_material.full_clean()
    competition_material.save()

    return competition_material


def create_competition_task(*,
                            name: str=None,
                            description: str=None,
                            gradable: bool=False,
                            existing_task: Task=None,
                            competition: Competition=None) -> CompetitionTask:
    competition_task = CompetitionTask(competition=competition)

    if existing_task is None:
        existing_task = Task(name=name, description=description, gradable=gradable)
        existing_task.full_clean()
        existing_task.save()

    competition_task.name = existing_task.name
    competition_task.description = existing_task.description
    competition_task.gradable = existing_task.gradable

    competition_task.task = existing_task
    competition_task.full_clean()
    competition_task.save()

    return competition_task


def create_gradable_solution(*,
                             task: CompetitionTask,
                             participant: CompetitionParticipant,
                             code: str=None,
                             file: BinaryIO=None) -> Solution:
    if code is not None and file is not None:
        raise ValidationError("Provide either code or a file, not both!")
    if code is None and file is None:
        raise ValidationError("Provide either code or a file!")
    if not CompetitionTest.objects.filter(task=task).exists():
        raise ValidationError("This task does not have tests yet")
    if code is not None:
        new_solution = Solution.objects.create(
            task=task,
            participant=participant,
            code=code,
            status=6
        )
    if file is not None:
        new_solution = Solution.objects.create(
            task=task,
            participant=participant,
            file=file,
            status=6
        )

    return new_solution


def create_non_gradable_solution(*,
                                 task: CompetitionTask,
                                 participant: CompetitionParticipant,
                                 url: str=None) -> Solution:
    if url is None:
            raise ValidationError("Provide a url!")
    new_solution = Solution.objects.create(
        task=task,
        participant=participant,
        url=url,
        status=6
    )

    return new_solution


def create_competition_test(*,
                            existing_test: Test=None,
                            task: CompetitionTask,
                            language: ProgrammingLanguage,
                            extra_options: Dict={},
                            code: str=None,
                            file: BinaryIO=None):
    new_test = CompetitionTest(task=task)
    if existing_test is None:
        existing_test = Test(language=language, extra_options=extra_options, code=code, file=file)
        existing_test.full_clean()
        existing_test.save()

    new_test.language = existing_test.language
    new_test.extra_options = existing_test.extra_options
    new_test.code = existing_test.code
    new_test.file = existing_test.file

    new_test.test = existing_test
    new_test.save()

    return new_test


def handle_competition_registration(*,
                                    email: str,
                                    full_name: str,
                                    competition: Competition) -> Tuple[bool, BaseUser]:
    """
    Handles competition registration and returns the registration token and True or
    False depending on whether further handling should be for an existing user or a
    new one.
    """
    user = BaseUser.objects.filter(email=email)
    registration_uuid = uuid.uuid4()
    if user.exists():
        user = user.first()
        user.competition_registration_uuid = registration_uuid
        user.save()
        if not hasattr(user, 'competitionparticipant'):
            participant = CompetitionParticipant.objects.create_from_user(user)
        else:
            participant = user.competitionparticipant
        handle_existing_user = True
    else:
        user = create_user(email=email,
                           registration_uuid=registration_uuid,
                           profile_data={'full_name': full_name})
        participant = CompetitionParticipant.objects.create_from_user(user)
        user.competition_registration_uuid = registration_uuid
        user.is_active = False
        user.save()
        handle_existing_user = False

    competition.participants.add(participant)

    return (handle_existing_user, user)


def handle_competition_login(*,
                             user: BaseUser,
                             registration_token: str) -> BaseUser:
    if not registration_token == str(user.competition_registration_uuid):
        raise ValidationError('URL token does not match User token')

    user.competition_registration_uuid = None
    user.save()

    return user
