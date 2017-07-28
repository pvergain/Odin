from test_plus import TestCase

from django.urls import reverse
from django.utils import timezone

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory
from odin.education.models import Teacher
from odin.education.factories import CourseFactory
from odin.education.services import add_teacher
from odin.applications.models import ApplicationInfo, ApplicationTask, IncludedApplicationTask
from odin.applications.factories import ApplicationInfoFactory


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

            self.assertRedirects(response,
                                 expected_url=reverse('dashboard:education:user-course-detail',
                                                      kwargs={'course_id': self.course.id}))
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

    def test_post_creates_only_included_task_when_existing_is_provided(self):
        add_teacher(course=self.course, teacher=self.teacher)
        existing_task = ApplicationTask.objects.create(name=self.task_name, description=self.task_description)
        current_app_task_count = ApplicationTask.objects.count()
        current_included_app_task_count = IncludedApplicationTask.objects.count()

        data = {
            'existing_task': existing_task.id,
            'name': self.task_name,
            'description': self.task_description
        }
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            self.assertRedirects(response, expected_url=reverse('dashboard:applications:edit-application-info',
                                                                kwargs={'course_id': self.course.id}))

        self.assertEqual(current_app_task_count, ApplicationTask.objects.count())
        self.assertEqual(current_included_app_task_count + 1, IncludedApplicationTask.objects.count())
