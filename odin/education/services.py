import tempfile
import os
import subprocess
import tarfile
import requests

from django.core.files import File
from django.conf import settings

from django.db import transaction
from django.db.models import Q, Sum, When, Case, IntegerField, F
from django.utils import timezone
from django.core.exceptions import ValidationError

from github import Github
from github.GithubException import UnknownObjectException

from datetime import datetime, timedelta, date

from typing import Dict, BinaryIO

from odin.users.models import BaseUser

from odin.grading.services import start_grader_communication

from .models import (
    Course,
    CourseAssignment,
    CourseDescription,
    Student,
    Teacher,
    Week,
    IncludedMaterial,
    Material,
    IncludedTask,
    Task,
    ProgrammingLanguage,
    Solution,
    Test,
    IncludedTest,
    StudentNote,
    Lecture,
    SolutionComment,
)


def add_student(course: Course, student: Student) -> CourseAssignment:
    return CourseAssignment.objects.create(course=course, student=student)


def add_teacher(course: Course, teacher: Teacher, hidden: bool=False) -> CourseAssignment:
    return CourseAssignment.objects.create(course=course, teacher=teacher, hidden=hidden)


@transaction.atomic
def create_course(
    *,
    name: str,
    start_date: datetime,
    end_date: datetime,
    repository: str,
    facebook_group: str=None,
    video_channel: str=None,
    slug_url: str=None,
    logo: BinaryIO=None,
    public: bool=True,
    attendable: bool=True,
    description: str=""
) -> Course:

    if Course.objects.filter(name=name).exists():
        raise ValidationError('Course already exists')

    course = Course.objects.create(
        name=name,
        start_date=start_date,
        end_date=end_date,
        repository=repository,
        facebook_group=facebook_group,
        video_channel=video_channel,
        slug_url=slug_url,
        logo=logo,
        public=public
    )

    weeks = course.duration_in_weeks
    start_date = course.start_date
    start_date = start_date - timedelta(days=start_date.weekday())

    week_instances = []
    for i in range(1, weeks + 1):
        current = Week(
            course=course,
            number=i,
            start_date=start_date,
            end_date=start_date + timedelta(days=6)
        )

        start_date = current.end_date + timedelta(days=1)
        week_instances.append(current)

    Week.objects.bulk_create(week_instances)
    CourseDescription.objects.create(course=course, verbose=description)

    return course


def create_included_material(
    *,
    course: Course,
    week: Week,
    identifier: str=None,
    url: str=None,
    content: str=None,
    existing_material: Material=None
) -> IncludedMaterial:

    included_material = IncludedMaterial(week=week, course=course)

    if existing_material is None:
        existing_material = Material(identifier=identifier, url=url, content=content)
        existing_material.full_clean()
        existing_material.save()

    included_material.identifier = existing_material.identifier
    included_material.url = existing_material.url
    included_material.content = existing_material.content

    included_material.material = existing_material
    included_material.full_clean()
    included_material.save()

    return included_material


def create_included_task(
    *,
    course: Course,
    week: Week,
    name: str=None,
    description: str=None,
    gradable: bool=False,
    existing_task: Task=None,
)-> IncludedTask:

    included_task = IncludedTask(week=week, course=course)
    if existing_task is None:
        existing_task = Task(name=name, description=description, gradable=gradable)
        existing_task.full_clean()
        existing_task.save()

    included_task.name = existing_task.name
    included_task.description = existing_task.description
    included_task.gradable = existing_task.gradable

    included_task.task = existing_task
    included_task.full_clean()
    included_task.save()

    return included_task


def create_test_for_task(
    *,
    existing_test: Test=None,
    task: IncludedTask,
    language: ProgrammingLanguage,
    extra_options: Dict={},
    code: str=None,
    requirements: str=None,
    file: BinaryIO=None
):

    new_test = IncludedTest(task=task)
    if existing_test is None:
        existing_test = Test(
            language=language,
            extra_options=extra_options,
            code=code,
            requirements=requirements,
            file=file
        )
        existing_test.full_clean()
        existing_test.save()

    new_test.language = existing_test.language
    new_test.extra_options = existing_test.extra_options
    new_test.code = existing_test.code
    new_test.requirements = existing_test.requirements
    new_test.file = existing_test.file

    new_test.test = existing_test
    new_test.save()

    return new_test


def create_gradable_solution(
    *,
    task: IncludedTask,
    user: BaseUser,
    code: str=None,
    file: File=None
) -> Solution:

    if code is not None and file is not None:
        raise ValidationError("Provide either code or a file, not both!")
    if code is None and file is None:
        raise ValidationError("Provide either code or a file!")
    if code is not None:
        new_solution = Solution.objects.create(
            task=task,
            user=user,
            code=code,
            status=6
        )
    if file is not None:
        new_solution = Solution.objects.create(
            task=task,
            user=user,
            status=6
        )
        new_solution.file.save(os.path.basename(file.name), file, save=True)

    return new_solution


def create_non_gradable_solution(
    *,
    task: IncludedTask,
    user: BaseUser,
    url: str=None
) -> Solution:

    if url is None:
            raise ValidationError("Provide a url!")
    new_solution = Solution.objects.create(
        task=task,
        user=user,
        url=url,
        status=6
    )

    return new_solution


def calculate_student_valid_solutions_for_course(
    *,
    user: BaseUser,
    course: Course
) -> str:

    total_tasks = IncludedTask.objects.filter(course=course).count()
    if not total_tasks:
        return 0
    solved_tasks = Solution.objects.get_solved_solutions_for_student_and_course(user, course).count()

    ratio = (solved_tasks/total_tasks) * 100
    return f'{ratio:.1f}'


def get_all_student_solution_statistics(
    *,
    task: IncludedTask
) -> Dict:

    result = {}
    course = task.course
    result['total_student_count'] = course.students.count()

    filters = {'solutions__task': task, 'solutions__isnull': False}
    result['students_with_a_submitted_solution_count'] = course.students.filter(**filters).distinct().count()
    q_expression = Q(solutions__task__gradable=True, solutions__status=Solution.OK) \
        | Q(solutions__task__gradable=False, solutions__status=Solution.SUBMITTED_WITHOUT_GRADING)
    result['students_with_a_passing_solution_count'] = course.students.filter(
        q_expression, solutions__task=task
    ).distinct().count()

    return result


def create_student_note(
    *,
    author: Teacher,
    assignment: CourseAssignment,
    text: str
) -> StudentNote:

    note = StudentNote(
        author=author,
        assignment=assignment,
        text=text
    )

    note.full_clean()
    note.save()

    return note


def create_lecture(
    *,
    date: date,
    course: Course
) -> Lecture:

    week_qs = Week.objects.filter(start_date__lte=date, end_date__gte=date, course=course)
    if week_qs.exists():
        lecture = Lecture(date=date, course=course, week=week_qs.first())
        lecture.full_clean()
        lecture.save()

        return lecture
    else:
        raise ValidationError('Date not in range of any week for this course')


def add_week_to_course(
    *,
    course: Course,
    new_end_date: timezone.datetime.date
) -> Week:

    last_week = course.weeks.last()
    new_week = Week.objects.create(
        course=course,
        number=last_week.number + 1,
        start_date=course.end_date,
        end_date=new_end_date
    )

    course.end_date = course.end_date + timezone.timedelta(days=7)
    course.save()

    return new_week


def create_solution_comment(
    *,
    solution: Solution,
    user: BaseUser,
    text: str
) -> SolutionComment:

    comment = SolutionComment(
        solution=solution,
        user=user,
        text=text
    )

    comment.full_clean()
    comment.save()

    return comment


def get_gradable_tasks_for_course(
    *,
    course: Course,
    user: BaseUser
):

    tasks = []

    for task in course.included_tasks.order_by('week__number', 'task__id'):
        if task.gradable:
            task.last_solution = get_last_solution_for_task(
                task=task,
                user=user
            )
            tasks.append(task)

    return tasks


def get_last_solution_for_task(
    *,
    task: IncludedTask,
    user: BaseUser
) -> Solution:

    return Solution.objects.filter(task=task, user=user).order_by('-id').first()


def create_included_task_with_test(
    *,
    course: Course,
    language: ProgrammingLanguage,
    week: Week,
    name: str,
    code: str,
    requirements: str=None,
    gradable: bool,
    description_url: str
):

    if not description_url.endswith('README.md'):
        description_url = description_url.replace('tree', 'blob')
        description_url = f'{description_url}/README.md'

    description_url = f'{description_url}?raw=1'

    markdown = requests.get(description_url, timeout=2).text

    included_task = create_included_task(
        course=course,
        week=week,
        name=name,
        description=markdown,
        gradable=gradable
    )
    included_task.save()

    if included_task.gradable:

        included_test = create_test_for_task(
            task=included_task,
            code=code,
            language=language,
            requirements=requirements
        )

        included_test.save()

    return included_task


def get_user_solution_summary(
    user: BaseUser
):

    results = Solution.objects.aggregate(
        OK=Sum(
            Case(
                When(Q(status__in=['2']) & Q(user=user), then=1),
                output_field=IntegerField()
            )
        ),
        TOTAL=Sum(
            Case(
                When(Q(status__range=(0, 6)) & Q(user=user), then=1),
                output_field=IntegerField()
            )
        )
    )

    completed_tasks = user.solutions.filter(status=2).annotate(
        name=F('task__name'),
        task_id=F('task'),
        solution_id=F('id'),
        solution_code=F('code'),
        test_result=F('test_output')
    ).values('name', 'task_id', 'solution_code', 'test_result', 'solution_id')

    results['completed_tasks'] = completed_tasks

    return results


def get_user_avatar_url(
    user: BaseUser
):

    if not user.profile.full_image:
        return None

    return str(user.profile.full_image.url)


def get_random_string(length=8):
    from random import choice
    import string
    symbol_arrays = [string.ascii_lowercase, string.ascii_uppercase, string.digits]

    string = ''

    for i in range(length):
            string += choice(choice(symbol_arrays))

    return string


def get_valid_github_clone_url(
    *,
    github_url: str
) -> str:

    gh = Github()
    url_parts = github_url.split('/')
    full_name = '/'.join(url_parts[3:5])
    repo = gh.get_repo(full_name)

    try:
        return repo.clone_url

    except UnknownObjectException:
        raise ValidationError(f'{github_url} is not a valid GitHub repo')


def create_solution_file(clone_url):

    with tempfile.TemporaryDirectory(prefix=f'{settings.MEDIA_ROOT}/solutions/', dir='') as tmpdir:
        path = f'{tmpdir}/solution'
        subprocess.run(['git', 'clone', clone_url, path])

        with tarfile.open(name=f'{tmpdir}/solution_{get_random_string()}.tar.gz', mode='w:gz') as tar:
            for file in os.listdir(path):
                tar.add(f'{path}/{file}', arcname=file)

        return File(open(tar.name, 'rb'))


def create_solution(
    user: BaseUser,
    task: IncludedTask,
    code: str=None,
    url: str=None,
) -> Solution:

    if code is None and url is None:
        raise ValidationError('Code or URL needed in order to create solution')

    if task.gradable and code:
        solution = create_gradable_solution(
            user=user,
            task=task,
            code=code,
        )

        start_grader_communication(
            solution_id=solution.id,
            solution_model='education.Solution'
        )

        if url:
            solution.url = url
            solution.save()

    elif task.gradable and url and not code:
        raise ValidationError('Cannot submit gradable solution from URL')

    elif not task.gradable and code or not code:
        if url:
            solution = create_non_gradable_solution(
                user=user,
                task=task,
                url=url
            )

            solution.code = code
            solution.save()

        else:
            solution = create_gradable_solution(
                user=user,
                task=task,
                code=code
            )

    return solution
