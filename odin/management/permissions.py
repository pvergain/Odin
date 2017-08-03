from odin.common.mixins import BaseUserPassesTestMixin


class DashboardManagementPermission(BaseUserPassesTestMixin):
    raise_exception = True
    permission_denied_message = 'You must be a superuser to access this panel.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        if self.request.user.is_superuser:
            return True and super().test_func()

        return False
