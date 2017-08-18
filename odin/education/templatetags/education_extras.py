import mistune

from django import template

from ..models import Student, Teacher, CourseAssignment

register = template.Library()


@register.filter(name='markdown')
def convert_from_markdown(text):
    md = mistune.Markdown()
    return md(text)


@register.filter(name='get_presence')
def get_course_presence(course, user):
    student = Student.objects.filter(user=user)
    teacher = Teacher.objects.filter(user=user)

    if student.exists():
        student = student.first()
        course_assignment = CourseAssignment.objects.filter(course=course, student=student)
        if course_assignment.exists():
            return f'{course_assignment.first().student_presence} %'

    if teacher.exists():
        teacher = teacher.first()
        course_assignment = CourseAssignment.objects.filter(course=course, teacher=teacher)
        if course_assignment.exists():
            return f'{course_assignment.first().student_presence} %'
