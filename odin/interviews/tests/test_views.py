from test_plus import TestCase

from django.urls import reverse
from django.utils import timezone

from odin.common.faker import faker

from odin.users.factories import BaseUserFactory

from odin.applications.factories import ApplicationFactory, ApplicationInfoFactory

from ..factories import InterviewFactory, InterviewerFreeTimeFactory
from ..models import Interviewer, Interview, InterviewerFreeTime


class TestChooseInterviewView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.application = ApplicationFactory(user=self.user)
        self.application_info = ApplicationInfoFactory()
        self.interviewer = Interviewer.objects.create_from_user(self.user)
        self.interview = InterviewFactory(application=self.application)
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
            url = reverse('dashboard:interviews:confirm-interview',
                          kwargs={
                              'application_id': self.application.id,
                              'interview_token': self.interview.uuid
                          })
            self.assertRedirects(response, expected_url=url)

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


class TestInterviewsListView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.interviewer = Interviewer.objects.create_from_user(self.user)
        self.interview = InterviewFactory(interviewer=self.interviewer)
        self.url = reverse('dashboard:interviews:user-interviews')

    def test_access_is_forbidden_if_not_interviewer(self):
        other_user = BaseUserFactory(password=self.test_password)
        with self.login(email=other_user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_access_is_allowed_if_interviewer(self):
        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_interviews_are_displayed_correctly_for_interviewer(self):
        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(list(Interview.objects.all()), list(response.context['object_list']))


class TestCreateFreeTimeView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.interviewer = Interviewer.objects.create_from_user(self.user)
        self.url = reverse('dashboard:interviews:add-free-time')

    def test_can_add_free_time_if_interviewer(self):
        free_time_count = InterviewerFreeTime.objects.count()
        start_time = faker.time_object()
        end_time = (timezone.datetime.combine(timezone.now(), start_time) + timezone.timedelta(seconds=1)).time()
        data = {
            'date': (timezone.now() + timezone.timedelta(days=1)).date(),
            'start_time': start_time,
            'end_time': end_time,
            'buffer_time': False
        }

        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertEqual(302, response.status_code)
            self.assertEqual(free_time_count + 1, InterviewerFreeTime.objects.count())
            self.assertIsNotNone(self.interviewer.free_time_slots)

    def test_cant_add_free_time_if_not_interviewer(self):
        other_user = BaseUserFactory(password=self.test_password)
        with self.login(email=other_user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)


class TestUpdateFreeTimeView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.interviewer = Interviewer.objects.create_from_user(self.user)
        self.interviewer_free_time = InterviewerFreeTimeFactory(interviewer=self.interviewer)
        self.url = reverse('dashboard:interviews:edit-free-time',
                           kwargs={'free_time_id': self.interviewer_free_time.id})

    def test_cannot_access_other_interviewer_free_time_details(self):
        user = BaseUserFactory(password=self.test_password)
        interviewer = Interviewer.objects.create_from_user(user)

        with self.login(email=interviewer.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_cannot_update_other_interviewer_free_time(self):
        user = BaseUserFactory(password=self.test_password)
        interviewer = Interviewer.objects.create_from_user(user)

        with self.login(email=interviewer.email, password=self.test_password):
            response = self.post(self.url, data={})
            self.assertEqual(403, response.status_code)

    def test_can_update_personal_free_time_successfully(self):
        old_date = self.interviewer_free_time.date
        data = {
            'date': old_date + timezone.timedelta(days=1),
            'start_time': self.interviewer_free_time.start_time,
            'end_time': self.interviewer_free_time.end_time,
        }

        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertEqual(302, response.status_code)
            self.interviewer_free_time.refresh_from_db()
            self.assertEqual(old_date + timezone.timedelta(days=1), self.interviewer_free_time.date)


class TestDeleteFreeTimeView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.interviewer = Interviewer.objects.create_from_user(self.user)
        self.interviewer_free_time = InterviewerFreeTimeFactory(interviewer=self.interviewer)
        self.url = reverse('dashboard:interviews:delete-free-time',
                           kwargs={'free_time_id': self.interviewer_free_time.id})

    def test_cannot_get_delete_free_time_view(self):
        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(405, response.status_code)

    def test_cannot_delete_free_time_if_not_interviewer(self):
        user = BaseUserFactory(password=self.test_password)

        with self.login(email=user.email, password=self.test_password):
            response = self.post(self.url)
            self.assertEqual(403, response.status_code)

    def test_cannot_delete_other_interviewer_free_time(self):
        user = BaseUserFactory(password=self.test_password)
        interviewer = Interviewer.objects.create_from_user(user)

        with self.login(email=interviewer.email, password=self.test_password):
            response = self.post(self.url)
            self.assertEqual(403, response.status_code)

    def test_can_delete_personal_free_time_if_interviewer(self):
        free_time_count = InterviewerFreeTime.objects.count()
        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.post(self.url)
            self.assertEqual(302, response.status_code)
            self.assertEqual(free_time_count - 1, InterviewerFreeTime.objects.count())
            self.assertEquals([], list(self.interviewer.free_time_slots.all()))
