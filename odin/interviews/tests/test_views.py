from test_plus import TestCase

from django.urls import reverse
from django.utils import timezone

from odin.common.faker import faker

from odin.users.factories import BaseUserFactory, SuperUserFactory
from odin.applications.factories import ApplicationFactory, ApplicationInfoFactory
from odin.applications.models import Application
from odin.interviews.factories import InterviewFactory, InterviewerFreeTimeFactory
from odin.interviews.models import Interviewer, Interview, InterviewerFreeTime


class TestChooseInterviewView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.application_info = ApplicationInfoFactory()
        self.application = ApplicationFactory(user=self.user, application_info=self.application_info)
        self.interviewer = Interviewer.objects.create_from_user(self.user)
        self.interview = InterviewFactory(application=self.application, interviewer=self.interviewer)
        self.url = reverse('dashboard:interviews:choose-interview',
                           kwargs={
                               'application_id': self.application.id,
                               'interview_token': self.interview.uuid
                           })

    def test_get_is_forbidden_when_application_user_does_not_match_request_user(self):
        new_user = BaseUserFactory()
        new_application = ApplicationFactory(user=new_user, application_info=self.application_info)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(reverse('dashboard:interviews:choose-interview',
                                        kwargs={
                                            'application_id': new_application.id,
                                            'interview_token': self.interview.uuid
                                        }))
            self.response_403(response=response)

    def test_get_is_forbidden_when_interview_does_not_match_application(self):
        new_user = BaseUserFactory()
        new_application = ApplicationFactory(user=new_user, application_info=self.application_info)
        new_interview = InterviewFactory(application=new_application, interviewer=self.interviewer)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(reverse('dashboard:interviews:choose-interview',
                                        kwargs={
                                            'application_id': new_application.id,
                                            'interview_token': new_interview.uuid
                                        }))
            self.response_403(response=response)

    def test_get_redirects_when_user_has_a_confirmed_interview_for_course(self):
        self.interview.has_confirmed = True
        self.interview.save()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)

            self.assertRedirects(response=response, expected_url=reverse('dashboard:interviews:confirm-interview',
                                                                         kwargs={
                                                                             'application_id': self.application.id,
                                                                             'interview_token': self.interview.uuid
                                                                         }))

    def test_post_confirms_newly_chosen_interview_and_redirects(self):
        new_interview = InterviewFactory(application=None, interviewer=self.interviewer)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(reverse('dashboard:interviews:choose-interview',
                                         kwargs={
                                            'application_id': self.application.id,
                                            'interview_token': new_interview.uuid
                                         }))
            new_interview.refresh_from_db()
            self.assertRedirects(response=response, expected_url=reverse('dashboard:interviews:confirm-interview',
                                                                         kwargs={
                                                                             'application_id': self.application.id,
                                                                             'interview_token': new_interview.uuid
                                                                         }))
            self.assertTrue(new_interview.has_confirmed)

    def test_post_redirects_when_user_already_has_a_confirmed_interview_for_course(self):
        self.interview.has_confirmed = True
        self.interview.save()
        new_interview = InterviewFactory(application=None, interviewer=self.interviewer)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(reverse('dashboard:interviews:choose-interview',
                                         kwargs={
                                            'application_id': self.application.id,
                                            'interview_token': new_interview.uuid
                                         }))
            new_interview.refresh_from_db()
            self.assertRedirects(response=response, expected_url=reverse('dashboard:interviews:confirm-interview',
                                                                         kwargs={
                                                                             'application_id': self.application.id,
                                                                             'interview_token': self.interview.uuid
                                                                         }))
            self.assertFalse(new_interview.has_confirmed)

    def test_get_returns_404_when_given_application_does_not_exist(self):
        non_existing_application_id = Application.objects.last().id + 1

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(reverse('dashboard:interviews:choose-interview',
                                        kwargs={
                                            'application_id': non_existing_application_id,
                                            'interview_token': self.interview.uuid
                                         }))
            self.response_404(response)


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

    def test_access_is_allowed_if_superuser(self):
        superuser = SuperUserFactory(password=self.test_password)

        with self.login(email=superuser.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_access_is_allowed_if_superuser_and_interviewer(self):
        self.interviewer.is_superuser = True
        self.interviewer.save()

        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

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


class TestConfirmInterviewView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.application_info = ApplicationInfoFactory()
        self.application = ApplicationFactory(user=self.user, application_info=self.application_info)
        self.interviewer = Interviewer.objects.create_from_user(self.user)
        self.interview = InterviewFactory(application=self.application, interviewer=self.interviewer)

    def test_post_does_not_confirm_given_interview_if_user_already_has_a_confirmed_interview(self):
        self.interview.has_confirmed = True
        self.interview.save()
        new_interview = InterviewFactory(application=None, interviewer=self.interviewer)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(reverse('dashboard:interviews:confirm-interview',
                                         kwargs={
                                             'application_id': self.application.id,
                                             'interview_token': new_interview.uuid
                                         }))

            new_interview.refresh_from_db()
            self.response_200(response)
            self.assertFalse(new_interview.has_confirmed)

    def test_post_confirms_given_interview_if_user_has_not_confirmed_his_interview(self):
        new_interview = InterviewFactory(application=None, interviewer=self.interviewer)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(reverse('dashboard:interviews:confirm-interview',
                                         kwargs={
                                             'application_id': self.application.id,
                                             'interview_token': new_interview.uuid
                                         }))

            new_interview.refresh_from_db()
            self.response_200(response)
            self.assertTrue(new_interview.has_confirmed)


class TestRateInterviewView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.application_info = ApplicationInfoFactory()
        self.application = ApplicationFactory(user=self.user, application_info=self.application_info)
        self.interviewer = Interviewer.objects.create_from_user(self.user)
        self.interview = InterviewFactory(application=self.application, interviewer=self.interviewer)
        self.url = reverse('dashboard:interviews:rate-interview',
                           kwargs={
                               'interview_token': self.interview.uuid
                           })

    def test_interviewer_can_not_rate_interview_that_he_is_not_interviewer_for(self):
        new_interviewer = Interviewer.objects.create_from_user(BaseUserFactory())
        new_interview = InterviewFactory(interviewer=new_interviewer)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(reverse('dashboard:interviews:rate-interview',
                                        kwargs={'interview_token': new_interview.uuid}))

            self.response_403(response)


class TestPromoteAcceptedUsersToStudentsView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)
        Interviewer.objects.create_from_user(self.user)
        self.application_info = ApplicationInfoFactory(
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            start_interview_date=timezone.now().date(),
            end_interview_date=timezone.now().date() + timezone.timedelta(days=faker.pyint()))
        self.url = reverse('dashboard:interviews:assign-accepted-users')

    def test_get_not_allowed(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.response_405(response)

    def test_post_forbidden_when_user_not_superuser(self):
        new_user = BaseUserFactory(password=self.test_password)
        Interviewer.objects.create_from_user(new_user)

        with self.login(email=new_user.email, password=self.test_password):
            response = self.post(self.url)
            self.response_403(response)
