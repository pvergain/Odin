from test_plus import TestCase

from odin.applications.factories import ApplicationFactory, ApplicationInfoFactory
from odin.users.factories import BaseUserFactory
from odin.education.factories import CourseFactory

from ..models import Interview
from ..factories import InterviewFactory


class TestInterviews(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()
        self.course = CourseFactory()
        self.application_info = ApplicationInfoFactory(course=self.course)
        self.application = ApplicationFactory(application_info=self.application_info, user=self.user)

    def test_with_application_returns_interviews_with_an_application(self):
        interviews_with_application_count = Interview.objects.with_application().count()

        InterviewFactory(application=self.application)
        InterviewFactory(application=None)

        self.assertEqual(interviews_with_application_count + 1, Interview.objects.with_application().count())

    def test_confirmed_for_returns_interviews_that_are_confirmed_for_course_application_info(self):
        confirmed_interviews = Interview.objects.confirmed_for(self.application_info).count()

        InterviewFactory(has_confirmed=True, application=self.application)
        InterviewFactory(has_confirmed=False, application=self.application)

        self.assertEqual(confirmed_interviews + 1, Interview.objects.confirmed_for(self.application_info).count())

    def test_confirmed_interviews_on_returns_confirmed_interviews_for_user_and_course_application_info(self):
        confirmed_interviews_for_user = Interview.objects.confirmed_interviews_on(self.user).count()

        InterviewFactory(has_confirmed=True, application=self.application)
        InterviewFactory(has_confirmed=False, application=self.application)

        self.assertEqual(confirmed_interviews_for_user + 1,
                         Interview.objects.confirmed_interviews_on(self.user).count())
