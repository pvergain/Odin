from test_plus import TestCase
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from django.test.utils import override_settings

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory
from odin.education.models import Teacher, Course
from odin.education.factories import CourseFactory
from odin.education.services import add_teacher
from odin.applications.models import (
    ApplicationInfo,
    ApplicationTask,
    IncludedApplicationTask,
    Application
)
from odin.applications.factories import (
    ApplicationInfoFactory,
    IncludedApplicationTaskFactory,
    ApplicationFactory,
    ApplicationTaskFactory,
    ApplicationSolutionFactory
)
from odin.applications.services import create_application


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
        self.course.start_date = timezone.now().date() - timezone.timedelta(days=faker.pyint())
        self.course.save()
        current_app_info_count = ApplicationInfo.objects.count()
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertFalse(response.context_data['form'].is_valid())
            self.assertEqual(current_app_info_count, ApplicationInfo.objects.count())


class TestCreateIncludedApplicationTaskView(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.app_info = ApplicationInfoFactory(course=self.course)
        self.task_name = faker.word()
        self.task_description = faker.text()
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.teacher = Teacher.objects.create_from_user(self.user)
        self.url = reverse('dashboard:applications:add-application-task',
                           kwargs={'course_id': self.course.id})

    def test_post_is_forbidden_if_not_teacher_in_course(self):
        data = {
            'name': self.task_name,
            'description': self.task_description
        }
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.response_403(response)

    def test_post_creates_task_and_included_task_when_existing_is_not_provided(self):
        add_teacher(course=self.course, teacher=self.teacher)
        data = {
            'name': self.task_name,
            'description': self.task_description
        }
        current_app_task_count = ApplicationTask.objects.count()
        current_included_app_task_count = IncludedApplicationTask.objects.count()
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            self.assertRedirects(response, expected_url=reverse('dashboard:applications:edit-application-info',
                                                                kwargs={'course_id': self.course.id}))

        self.assertEqual(current_app_task_count + 1, ApplicationTask.objects.count())
        self.assertEqual(current_included_app_task_count + 1, IncludedApplicationTask.objects.count())


class TestAddInclduedApplicationTaskFromExistingView(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.app_info = ApplicationInfoFactory(course=self.course)
        self.task_name = faker.word()
        self.task_description = faker.text()
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.teacher = Teacher.objects.create_from_user(self.user)
        self.url = reverse('dashboard:applications:add-application-task-from-existing',
                           kwargs={'course_id': self.course.id})

    def test_post_creates_only_included_task_when_existing_is_provided(self):
        add_teacher(course=self.course, teacher=self.teacher)
        existing_task = ApplicationTaskFactory(name=self.task_name, description=self.task_description)
        current_app_task_count = ApplicationTask.objects.count()
        current_included_app_task_count = IncludedApplicationTask.objects.count()

        data = {
            'task': existing_task.id,
        }
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            self.assertRedirects(response, expected_url=reverse('dashboard:applications:edit-application-info',
                                                                kwargs={'course_id': self.course.id}))

            self.assertEqual(current_app_task_count, ApplicationTask.objects.count())
            self.assertEqual(current_included_app_task_count + 1, IncludedApplicationTask.objects.count())

    def test_post_does_not_create_included_task_when_it_is_already_added_to_course(self):
        add_teacher(course=self.course, teacher=self.teacher)
        task = IncludedApplicationTaskFactory(application_info=self.app_info)
        current_app_task_count = ApplicationTask.objects.count()
        current_included_app_task_count = IncludedApplicationTask.objects.count()

        data = {
            'task': task.task.id
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            self.assertRedirects(response, expected_url=reverse('dashboard:applications:edit-application-info',
                                                                kwargs={'course_id': self.course.id}))
            self.assertEqual(current_app_task_count, ApplicationTask.objects.count())
            self.assertEqual(current_included_app_task_count, IncludedApplicationTask.objects.count())

    def test_post_with_task_created_from_different_course_creates_only_included_task_for_the_new_course(self):
        add_teacher(course=self.course, teacher=self.teacher)
        task = IncludedApplicationTaskFactory(application_info=self.app_info)
        current_app_task_count = ApplicationTask.objects.count()
        current_included_app_task_count = IncludedApplicationTask.objects.count()

        new_course = CourseFactory()
        add_teacher(course=new_course, teacher=self.teacher)
        ApplicationInfoFactory(course=new_course)
        new_url = reverse('dashboard:applications:add-application-task-from-existing',
                          kwargs={'course_id': new_course.id})
        data = {
            'task': task.task.id
        }
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(new_url, data=data)
            self.assertRedirects(response, expected_url=reverse('dashboard:applications:edit-application-info',
                                                                kwargs={'course_id': new_course.id}))
            self.assertEqual(current_app_task_count, ApplicationTask.objects.count())
            self.assertEqual(current_included_app_task_count + 1, IncludedApplicationTask.objects.count())
            self.assertEqual(IncludedApplicationTask.objects.last().application_info.id, new_course.application_info.id)


class TestApplyToCourseView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.user.is_active = True
        self.user.save()
        self.course = CourseFactory()
        self.app_info = ApplicationInfoFactory(course=self.course,
                                               start_date=timezone.now().date())
        self.url = reverse('dashboard:applications:apply-to-course', kwargs={'course_id': self.course.id})

    def test_post_successfully_creates_application_when_apply_is_open(self):
        self.app_info.start_date = timezone.now().date()
        self.app_info.end_date = timezone.now().date() + timezone.timedelta(days=2)
        self.app_info.save()

        current_app_count = Application.objects.count()
        data = {
            'phone': faker.phone_number(),
            'works_at': faker.job()
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

        create_application(user=self.user, application_info=self.app_info)
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertRedirects(response,
                                 expected_url=reverse('dashboard:applications:edit-application',
                                                      kwargs={'course_id': self.course.id}))

    def test_post_redirects_when_user_has_already_applied(self):
        self.app_info.start_date = timezone.now().date()
        self.app_info.end_date = timezone.now().date() + timezone.timedelta(days=2)
        self.app_info.save()

        data = {
            'phone': faker.phone_number(),
            'works_at': faker.job()
        }

        create_application(user=self.user, application_info=self.app_info)
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            expected_url = reverse('dashboard:applications:edit-application',
                                   kwargs={'course_id': self.course.id})
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
            'phone': faker.phone_number(),
            'works_at': faker.job()
        }
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertRedirects(response, expected_url=reverse('dashboard:applications:user-applications'))
            self.assertEqual(mock_send_mail.called, True)
            (template_name, recipients, context), kwargs = mock_send_mail.call_args
            self.assertEqual([self.user.email], recipients)


class TestEditApplicationView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.user.is_active = True
        self.user.save()
        self.course = CourseFactory()
        self.app_info = ApplicationInfoFactory(course=self.course,
                                               start_date=timezone.now().date(),
                                               end_date=timezone.now().date() + timezone.timedelta(days=2))
        self.application = ApplicationFactory(user=self.user, application_info=self.app_info)
        self.url = reverse('dashboard:applications:edit-application',
                           kwargs={'course_id': self.course.id})
        self.success_url = reverse('dashboard:applications:user-applications')

    def test_update_works_without_submitted_tasks(self):
        IncludedApplicationTaskFactory(application_info=self.app_info)
        previous_works_at = self.application.works_at
        new_works_at = str(faker.pyint()) + faker.job()

        data = {
            'phone': faker.phone_number(),
            'works_at': new_works_at
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertRedirects(response, expected_url=self.success_url)
            self.application.refresh_from_db()
            self.assertNotEqual(previous_works_at, self.application.works_at)
            self.assertEqual(new_works_at, self.application.works_at)

    def test_update_works_with_multiple_submitted_tasks(self):
        tasks = ApplicationTaskFactory.create_batch(5)
        app_tasks = []
        for task in tasks:
            app_tasks.append(IncludedApplicationTaskFactory(task=task, application_info=self.app_info))
        data = {task.name: faker.url() for task in app_tasks}
        data['phone'] = faker.phone_number()
        data['works_at'] = faker.job()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertRedirects(response, expected_url=self.success_url)
            self.application.refresh_from_db()
            self.assertEqual(len(tasks), self.application.solutions.count())
            for solution in self.application.solutions.all():
                self.assertIsNotNone(solution)
                self.assertIsNotNone(solution.url)

    def test_form_has_initial_data_for_solutions_when_user_has_submitted(self):
        task = ApplicationTaskFactory()
        app_task = IncludedApplicationTaskFactory(task=task, application_info=self.app_info)
        solution = ApplicationSolutionFactory(task=app_task, application=self.application)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(solution.url, response.context_data['form'].initial[app_task.name])

    def test_get_returns_404_when_application_does_not_exist(self):
        fake_course_id = Course.objects.last().id + faker.pyint()
        self.url = reverse('dashboard:applications:edit-application',
                           kwargs={'course_id': fake_course_id})

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.response_404(response)

    def test_get_returns_403_when_application_info_has_external_application_form(self):
        self.app_info.external_application_form = faker.url()
        self.app_info.save()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.response_403(response)
