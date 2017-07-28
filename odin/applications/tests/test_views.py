from test_plus import TestCase

from django.urls import reverse
from django.utils import timezone

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory
from odin.education.models import Teacher
from odin.education.factories import CourseFactory
from odin.education.services import add_teacher
from odin.applications.models import ApplicationInfo


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
