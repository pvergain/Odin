import os

from test_plus import TestCase

from ..models import Profile, BaseUser
from ..factories import BaseUserFactory

from odin.education.models import Teacher, Course
from odin.education.factories import CourseFactory

from odin.common.faker import faker


class ProfileSignalTests(TestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    def test_create_user_creates_profile(self):
        self.assertEqual(Profile.objects.count(), 0)
        BaseUserFactory()
        self.assertEqual(Profile.objects.count(), 1)

    def test_sign_up_request_creates_profile(self):
        url = self.reverse('account_signup')
        password = "1234asdf"
        data = {
            'email': faker.email(),
            'password1': password,
            'password2': password,
            'g-recaptcha-response': 'PASSED'
        }
        self.assertEqual(Profile.objects.count(), 0)

        response = self.post(url_name=url, data=data, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Profile.objects.count(), 1)


class SuperUserSignalTest(TestCase):

    def test_create_superuser_creates_teacher(self):
        self.assertEqual(0, Teacher.objects.count())
        BaseUser.objects.create_superuser(email=faker.email(), password=faker.password())
        self.assertEqual(1, Teacher.objects.count())

    def test_create_superuser_adds_teacher_to_old_courses(self):
        CourseFactory.create_batch(5)
        user = BaseUser.objects.create_superuser(email=faker.email(), password=faker.password())
        user = user.teacher
        courses = Course.objects.all()
        for course in courses:
            self.assertIn(member=user, container=course.teachers.all())
