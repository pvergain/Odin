from odin.common.mixins import BaseUserPassesTestMixin


class ViewApplicationDetailPermission(BaseUserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        teaches_course = self.get_object().application_info.course.teachers.filter(user=user).exists()
        if teaches_course or user.is_interviewer():
            return True and super().test_func()

        return False
