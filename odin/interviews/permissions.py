from django.shortcuts import get_object_or_404

from odin.common.mixins import BaseUserPassesTestMixin
from odin.applications.models import Application

from .models import Interview, Interviewer


class CannotConfirmOthersInterviewPermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        uuid = self.kwargs.get('interview_token')
        application_id = self.kwargs.get('application_id')
        self.interview = get_object_or_404(Interview, uuid=uuid)
        self.application = get_object_or_404(Application, id=application_id)
        self.interviewer = get_object_or_404(Interviewer, interview=self.interview)

        if self.interview.application is not None:
            if self.interview not in self.application.interview_set.all():
                return False

        if self.application not in self.request.user.applications.all():
            return False

        return True and super().test_func()


class IsInterviewerPermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if self.request.user.is_interviewer():
            return True and super().test_func()

        return False


class CannotControlOtherInterviewerDataPermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not (self.request.user.interviewer == self.get_object().interviewer):
            return False

        return True and super().test_func()
