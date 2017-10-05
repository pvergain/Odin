from rest_framework.permissions import BasePermission

from django.shortcuts import get_object_or_404

from odin.common.mixins import BaseUserPassesTestMixin
from odin.education.models import Course


class IsStudentOrTeacherInCoursePermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        course = self.course
        email = self.request.user.email
        self.is_student = course.students.filter(email=email).exists()
        self.is_teacher = course.teachers.filter(email=email).exists()

        if self.is_student or self.is_teacher:
            return True and super().test_func()

        return False


class IsTeacherInCoursePermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        email = self.request.user.email
        self.is_teacher = self.course.teachers.filter(email=email).exists()
        if self.is_teacher:
            return True and super().test_func()

        return False


class IsStudentInCoursePermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        is_student = self.course.students.filter(email=user.email).exists()
        if is_student:
            return True and super().test_func()

        return False


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
