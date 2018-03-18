from rest_framework.permissions import BasePermission

from django.shortcuts import get_object_or_404

from odin.education.models import Course


class IsStudentOrTeacherInCourseAPIPermission(BasePermission):
    message = 'Need to be student or a teacher in the course'

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        course_id = view.kwargs.get('course_id')
        if course_id:
            course = get_object_or_404(Course, id=course_id)
        else:
            course = view.get_object().task.topic.course
        email = request.user.email
        is_teacher = course.teachers.filter(email=email).exists()
        is_solution_author = False

        if request.user.is_student():
            is_solution_author = view.get_object().student == request.user.student
        if is_solution_author or is_teacher:
            return True

        return False
