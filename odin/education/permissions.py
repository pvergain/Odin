from odin.common.mixins import BaseUserPassesTestMixin


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
            return True

        return False
