from odin.management.permissions import BaseUserPassesTestMixin


class CourseDetailPermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        course = self.get_object()
        email = self.request.user.email
        is_student = course.students.filter(email=email).exists()
        is_teacher = course.teachers.filter(email=email).exists()

        if is_student or is_teacher:
            return True and super().test_func()

        return False
