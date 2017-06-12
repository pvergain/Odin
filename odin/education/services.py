from .models import CourseAssignment


def add_student(course, student):
    return CourseAssignment.objects.create(course=course, student=student)


def add_teacher(course, teacher):
    return CourseAssignment.objects.create(course=course, teacher=teacher)
