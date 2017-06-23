from odin.common.mixins import BaseUserPassesTestMixin


class DashboardManagementPermission(BaseUserPassesTestMixin):
    raise_exception = True
    permission_denied_message = 'You must be a superuser to access this panel.'

    def test_func(self):
        if not self.request.user.is_superuser:
            return False

        return True and super().test_func()
