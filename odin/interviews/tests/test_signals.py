from test_plus import TestCase

from odin.interviews.models import Interview
from odin.interviews.factories import InterviewFactory
from odin.applications.factories import ApplicationFactory


class TestDeleteInterviewDataInApplication(TestCase):
    def setUp(self):
        self.application = ApplicationFactory()
        self.interview = InterviewFactory(application=self.application)

    def test_signal_sets_has_interview_date_to_false_when_interview_is_deleted(self):
        Interview.objects.all().delete()
        self.application.refresh_from_db()

        self.assertFalse(self.application.has_interview_date)
