import mistune

from django import template
from django.db.models import Q

register = template.Library()


@register.filter(name='markdown')
def convert_from_markdown(text):
    md = mistune.Markdown()
    return md(text)


@register.filter(name='iterable_from_difference')
def iterable_from_difference(x, subtract_from):
    return range(subtract_from-x)


@register.filter(name='solved_tasks_for_course')
def solved_tasks_for_course(student, course):
    solved = student.solutions.get_solved_solutions_for_student_and_course(student=student, course=course)

    return solved.count()


@register.filter(name='passed_or_failed')
def passed_or_failed(task):
    q_expression = Q(task__gradable=True, status=2) | Q(task__gradable=False, status=6)
    if task.solutions.filter(q_expression).exists():
        return "Passed"

    if not task.solutions.all():
        return "Not submitted"

    return "Failed"
