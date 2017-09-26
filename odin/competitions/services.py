from typing import BinaryIO

from django.core.exceptions import ValidationError

from odin.education.models import Material, Task

from .models import CompetitionMaterial, Competition, CompetitionTask, CompetitionParticipant, Solution


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
