from test_plus import TestCase

from django.urls import reverse

from odin.common.faker import faker

from odin.users.factories import BaseUserFactory

from odin.applications.factories import ApplicationFactory, ApplicationInfoFactory

from ..factories import InterviewFactory, InterviewerFreeTimeFactory
from ..models import Interviewer


class TestChooseInterviewView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.application = ApplicationFactory(user=self.user)
        self.application_info = ApplicationInfoFactory()
        self.interviewer = Interviewer.objects.create_from_user(self.user)
        self.interview = InterviewFactory(application=self.application)
        self.interviewer_free_time = InterviewerFreeTimeFactory(interviewer=self.interviewer)
        self.url = reverse('dashboard:interviews:choose-interview',
                           kwargs={
                               'application_id': self.application.id,
                               'interview_token': self.interview.uuid
                           })

    def test_get_redirects_when_interview_is_already_confirmed(self):
        self.interview.has_confirmed = True
        self.interview.save()
        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(302, response.status_code)

    def test_get_forbidden_if_not_applicant_of_application(self):
        other_user = BaseUserFactory(password=self.test_password)
        self.application.user = other_user
        self.application.save()
        with self.login(email=other_user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_post_is_successful_with_valid_data(self):
        self.interviewer.courses_to_interview.add(self.application_info)
        self.interviewer.save()
        other_interview = InterviewFactory(application=None, interviewer=self.interviewer)
        data = {'interviews': other_interview.id}
        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertEqual(302, response.status_code)
            other_interview.refresh_from_db()
            self.interview.refresh_from_db()
            self.assertEqual(self.application, other_interview.application)
            self.assertNotEqual(self.application, self.interview.application)

    def test_message_is_displayed_on_selecting_already_taken_interview(self):
        self.interviewer.courses_to_interview.add(self.application_info)
        self.interviewer.save()
        other_application = ApplicationFactory()
        other_interview = InterviewFactory(application=other_application, interviewer=self.interviewer)
        data = {'interviews': other_interview.id}
        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertEqual(200, response.status_code)
            self.assertIsNotNone(response.context['form'].errors)
