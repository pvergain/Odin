from .mixins import BaseUserPassesTestMixin


class IsSuperuserPermission(BaseUserPassesTestMixin):

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return super().test_func()
