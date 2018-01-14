from test_plus import TestCase
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from django.test.utils import override_settings

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory, SuperUserFactory
from odin.interviews.models import Interviewer
from odin.interviews.services import add_course_to_interviewer_courses
from odin.education.models import Teacher
from odin.education.factories import CourseFactory
from odin.education.services import add_teacher

from ..models import (
    ApplicationInfo,
    Application
)
from ..factories import (
    ApplicationInfoFactory,
    ApplicationFactory
)
from ..services import create_application


class TestCreateApplicationInfoView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.teacher = Teacher.objects.create_from_user(self.user)
        self.start_date = faker.date_object()
        self.end_date = faker.date_object()
        self.course = CourseFactory()
        self.start_interview_date = faker.date_object()
        self.end_interview_date = faker.date_object()
        self.url = reverse('dashboard:applications:create-application-info',
                           kwargs={'course_id': self.course.id})

    def test_get_is_forbidden_if_not_teacher_for_course(self):
        response = self.get(self.url)
        self.response_403(response)

    def test_post_is_forbidden_if_not_teacher_in_course(self):
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            self.response_403(response)

    def test_get_ok_when_user_is_teacher_in_course(self):
        add_teacher(course=self.course, teacher=self.teacher)
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
        self.response_200(response)

    def test_post_does_not_create_instance_when_data_is_invalid(self):
        add_teacher(course=self.course, teacher=self.teacher)
        current_app_info_count = ApplicationInfo.objects.count()
        self.start_date = timezone.now().date() - timezone.timedelta(days=1)

        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            self.assertFalse(response.context_data['form'].is_valid())
            self.assertEqual(current_app_info_count, ApplicationInfo.objects.count())

    def test_post_creates_instance_when_data_is_valid(self):
        add_teacher(course=self.course, teacher=self.teacher)
        self.course.start_date = timezone.now().date() + timezone.timedelta(days=1)
        self.course.end_date = timezone.now().date() + timezone.timedelta(days=2)
        self.course.save()
        current_app_info_count = ApplicationInfo.objects.count()
        self.start_date = timezone.now().date() + timezone.timedelta(days=1)
        self.end_date = timezone.now().date() + timezone.timedelta(days=2)

        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            self.assertRedirects(response,
                                 expected_url=reverse('dashboard:education:user-course-detail',
                                                      kwargs={'course_id': self.course.id}))
            self.assertEqual(current_app_info_count + 1, ApplicationInfo.objects.count())

    def test_post_does_not_create_instance_when_course_has_already_started(self):
        add_teacher(course=self.course, teacher=self.teacher)
        current_app_info_count = ApplicationInfo.objects.count()
        data = {
            'start_date': self.course.start_date + timezone.timedelta(days=faker.pyint()),
            'end_date': self.end_date,
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertFalse(response.context_data['form'].is_valid())
            self.assertEqual(current_app_info_count, ApplicationInfo.objects.count())


class TestApplyToCourseView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.user.is_active = True
        self.user.save()
        self.course = CourseFactory()
        self.app_info = ApplicationInfoFactory(course=self.course,
                                               start_date=timezone.now().date(),
                                               competition=None)
        self.url = reverse('dashboard:applications:apply-to-course', kwargs={'course_slug': self.course.slug_url})

    def test_post_successfully_creates_application_when_apply_is_open(self):
        self.app_info.start_date = timezone.now().date()
        self.app_info.end_date = timezone.now().date() + timezone.timedelta(days=2)
        self.app_info.save()

        current_app_count = Application.objects.count()
        data = {
            'full_name': faker.name(),
            'phone': faker.phone_number(),
            'works_at': faker.job(),
            'skype': faker.word()
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertRedirects(response, expected_url=reverse('dashboard:applications:user-applications'))
            self.assertEqual(current_app_count + 1, Application.objects.count())

    def test_post_does_not_create_application_when_apply_is_closed(self):
        self.app_info.start_date = timezone.now().date() - timezone.timedelta(days=2)
        self.app_info.end_date = timezone.now().date() - timezone.timedelta(days=1)
        self.app_info.save()

        current_app_count = Application.objects.count()
        data = {
            'phone': faker.phone_number(),
            'works_at': faker.job()
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            self.assertFalse(response.context_data['form'].is_valid())
            self.assertEqual(current_app_count, Application.objects.count())

    def test_get_redirects_when_user_has_already_applied(self):
        self.app_info.start_date = timezone.now().date()
        self.app_info.end_date = timezone.now().date() + timezone.timedelta(days=2)
        self.app_info.save()

        create_application(user=self.user, application_info=self.app_info, skype=faker.word(), full_name=faker.name())
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertRedirects(response,
                                 expected_url=reverse('dashboard:applications:user-applications'))

    def test_post_redirects_when_user_has_already_applied(self):
        self.app_info.start_date = timezone.now().date()
        self.app_info.end_date = timezone.now().date() + timezone.timedelta(days=2)
        self.app_info.save()

        data = {
            'phone': faker.phone_number(),
            'works_at': faker.job(),
            'skype': faker.word()
        }

        create_application(user=self.user, application_info=self.app_info,
                           skype=data.get('skype'), full_name=faker.name())
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            expected_url = reverse('dashboard:applications:user-applications')
            self.assertRedirects(response,
                                 expected_url=expected_url)

    def test_view_redirects_to_external_url_when_external_application_form_is_provided(self):
        self.app_info.external_application_form = faker.url()
        self.app_info.save()
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertRedirects(response,
                                 expected_url=self.app_info.external_application_form,
                                 fetch_redirect_response=False)

    @override_settings(USE_DJANGO_EMAIL_BACKEND=False)
    @patch('odin.common.tasks.send_template_mail.delay')
    def test_sends_mail_to_address_upon_successful_application(self, mock_send_mail):
        self.app_info.start_date = timezone.now().date()
        self.app_info.end_date = timezone.now().date() + timezone.timedelta(days=2)
        self.app_info.save()

        data = {
            'full_name': faker.name(),
            'phone': faker.phone_number(),
            'works_at': faker.job(),
            'skype': faker.word
        }
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertRedirects(response, expected_url=reverse('dashboard:applications:user-applications'))
            self.assertEqual(mock_send_mail.called, True)
            (template_name, recipients, context), kwargs = mock_send_mail.call_args
            self.assertEqual([self.user.email], recipients)


class TestUserApplicationsListView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.user.is_active = True
        self.user.save()
        self.course = CourseFactory(
            start_date=timezone.now() + timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=20)
        )
        self.app_info = ApplicationInfoFactory(
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=4),
            start_interview_date=timezone.now() + timezone.timedelta(days=5),
            end_interview_date=timezone.now() + timezone.timedelta(days=6),
            course=self.course
        )
        self.application = ApplicationFactory(application_info=self.app_info, user=self.user)
        self.url = reverse('dashboard:applications:user-applications')

    def test_user_sees_his_applications_on_get(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)
            self.assertEqual([self.application], list(response.context['object_list']))

    def test_superuser_can_see_all_student_applications(self):
        superuser = SuperUserFactory(password=self.test_password)
        superuser.is_active = True
        superuser.save()

        with self.login(email=superuser.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)
            self.assertEqual(self.course, response.context['teached_courses'].first())


class TestApplicationDetailView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.user.is_active = True
        self.user.save()
        self.course = CourseFactory(
            start_date=timezone.now() + timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=20)
        )
        self.app_info = ApplicationInfoFactory(
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=4),
            start_interview_date=timezone.now() + timezone.timedelta(days=5),
            end_interview_date=timezone.now() + timezone.timedelta(days=6),
            course=self.course
        )
        self.application = ApplicationFactory(application_info=self.app_info, user=self.user)
        self.url = reverse('dashboard:applications:application-detail',
                           kwargs={'application_id': self.application.id})

    def test_can_not_view_application_detail_if_regular_user(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.response_403(response)

    def test_can_view_application_detail_if_only_teacher_and_not_interviewer_for_course(self):
        teacher = Teacher.objects.create_from_user(self.user)
        add_teacher(self.course, teacher)
        with self.login(email=teacher.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)
            self.assertEqual(self.application, response.context['object'])

    def test_can_view_application_detail_if_superuser_and_not_interviewer_for_course(self):
        superuser = SuperUserFactory(password=self.test_password)
        with self.login(email=superuser.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)
            self.assertEqual(self.application, response.context['object'])

    def test_can_view_application_detail_if_interviewer_for_course(self):
        interviewer = Interviewer.objects.create_from_user(self.user)
        add_course_to_interviewer_courses(interviewer=interviewer, course=self.course)
        with self.login(email=interviewer.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)
            self.assertEqual(self.application, response.context['object'])


class TestEditApplicationView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.user.is_active = True
        self.user.save()
        self.course = CourseFactory(
            start_date=timezone.now() + timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=20)
        )
        self.app_info = ApplicationInfoFactory(
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=4),
            start_interview_date=timezone.now() + timezone.timedelta(days=5),
            end_interview_date=timezone.now() + timezone.timedelta(days=6),
            course=self.course
        )
        self.application = ApplicationFactory(application_info=self.app_info, user=self.user)
        self.url = reverse('dashboard:applications:edit',
                           kwargs={
                               'course_slug': self.course.slug_url
                           })

    def test_get_returns_correct_application(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(response.context['object'], self.application)
