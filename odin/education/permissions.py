from odin.common.mixins import BaseUserPassesTestMixin


class IsStudentOrTeacherForCoursePermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        course = self.course
        email = self.request.user.email
        is_student = course.students.filter(email=email).exists()
        is_teacher = course.teachers.filter(email=email).exists()

        if is_student or is_teacher:
            return True and super().test_func()

        return False
