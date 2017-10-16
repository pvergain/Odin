import mistune

from django import template

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


@register.filter(name='get_date_for_weekday')
def get_date_for_weekday(dates, weekday):
    return dates.get(weekday, "No Lecture")
