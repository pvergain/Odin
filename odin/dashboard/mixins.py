from django.contrib.auth.mixins import UserPassesTestMixin

"""
COMMENT: This looks more like "permissions.py" then "mixins.py"
Also - no need to add Mixin at the end of the class since it's not mixin
"""


class BaseUserPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return True


class ManagementDashboardPermissionMixin(BaseUserPassesTestMixin):
    raise_exception = True
    permission_denied_message = 'You must be a superuser to access this panel.'

    def test_func(self):
        if not self.request.user.is_superuser:
            return False

        return True and super().test_func()
