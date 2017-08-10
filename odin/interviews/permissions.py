from odin.common.mixins import BaseUserPassesTestMixin

from odin.applications.models import Application

from .models import Interview, Interviewer


class CannotConfirmOthersInterviewPermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        uuid = self.kwargs.get('interview_token')
        application_id = self.kwargs.get('application_id')
        self.interview = Interview.objects.filter(uuid=uuid).first()
        self.application = Application.objects.filter(id=application_id).first()
        self.interviewer = Interviewer.objects.filter(interview=self.interview).first()

        if self.application.user != self.request.user or self.application_id != int(application_id):
            return False

        return True and super().test_func()
