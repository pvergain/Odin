from datetime import datetime, timedelta, date
from typing import Dict, BinaryIO

import requests
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError

from odin.users.models import BaseUser

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
def create_course(*,
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
                  description: str="") -> Course:

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
        current = Week(course=course,
                       number=i,
                       start_date=start_date,
                       end_date=start_date + timedelta(days=6))
        start_date = current.end_date + timedelta(days=1)
        week_instances.append(current)

    Week.objects.bulk_create(week_instances)
    CourseDescription.objects.create(course=course, verbose=description)

    return course


def create_included_material(*,
                             course: Course,
                             week: Week,
                             identifier: str=None,
                             url: str=None,
                             content: str=None,
                             existing_material: Material=None) -> IncludedMaterial:
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


def create_included_task(*,
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


def create_test_for_task(*,
                         existing_test: Test=None,
                         task: IncludedTask,
                         language: ProgrammingLanguage,
                         extra_options: Dict={},
                         code: str=None,
                         file: BinaryIO=None):
    new_test = IncludedTest(task=task)
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


def create_gradable_solution(*,
                             task: IncludedTask,
                             student: Student,
                             code: str=None,
                             file: BinaryIO=None) -> Solution:
    if code is not None and file is not None:
        raise ValidationError("Provide either code or a file, not both!")
    if code is None and file is None:
        raise ValidationError("Provide either code or a file!")
    if code is not None:
        new_solution = Solution.objects.create(
            task=task,
            student=student,
            code=code,
            status=6
        )
    if file is not None:
        new_solution = Solution.objects.create(
            task=task,
            student=student,
            file=file,
            status=6
        )

    return new_solution


def create_non_gradable_solution(*,
                                 task: IncludedTask,
                                 student: Student,
                                 url: str=None) -> Solution:
    if url is None:
            raise ValidationError("Provide a url!")
    new_solution = Solution.objects.create(
        task=task,
        student=student,
        url=url,
        status=6
    )

    return new_solution


def calculate_student_valid_solutions_for_course(*,
                                                 student: Student,
                                                 course: Course) -> str:
    total_tasks = IncludedTask.objects.filter(course=course).count()
    if not total_tasks:
        return 0
    solved_tasks = Solution.objects.get_solved_solutions_for_student_and_course(student, course).count()

    ratio = (solved_tasks/total_tasks) * 100
    return f'{ratio:.1f}'


def get_all_student_solution_statistics(*,
                                        task: IncludedTask) -> Dict:
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


def create_student_note(*,
                        author: Teacher,
                        assignment: CourseAssignment,
                        text: str) -> StudentNote:
    note = StudentNote(author=author,
                       assignment=assignment,
                       text=text)
    note.full_clean()
    note.save()

    return note


def create_lecture(*,
                   date: date,
                   course: Course) -> Lecture:
    week_qs = Week.objects.filter(start_date__lte=date, end_date__gte=date, course=course)
    if week_qs.exists():
        lecture = Lecture(date=date, course=course, week=week_qs.first())
        lecture.full_clean()
        lecture.save()

        return lecture
    else:
        raise ValidationError('Date not in range of any week for this course')


def add_week_to_course(*,
                       course: Course,
                       new_end_date: timezone.datetime.date) -> Week:
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


def create_solution_comment(*,
                            solution: Solution,
                            user: BaseUser,
                            text: str) -> SolutionComment:
    comment = SolutionComment(solution=solution,
                              user=user,
                              text=text)
    comment.full_clean()
    comment.save()

    return comment


def get_gradable_tasks_for_course(*, course: Course, student: Student):
    tasks = []

    for task in course.included_tasks.all():
        if task.gradable:
            task.last_solution = get_last_solution_for_task(
                task=task,
                student=student
            )
            tasks.append(task)

    return tasks


def get_last_solution_for_task(*, task: IncludedTask, student: Student) -> Solution:
    return Solution.objects.filter(task=task, student=student).order_by('-id').first()


def create_included_task_with_test(
    *,
    course: Course,
    language: ProgrammingLanguage,
    week: Week,
    name: str,
    code: str,
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
            language=language
        )
        included_test.save()

    return included_task
