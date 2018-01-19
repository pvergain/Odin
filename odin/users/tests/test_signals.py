import os

from test_plus import TestCase

from ..models import Profile, BaseUser
from ..factories import BaseUserFactory

from odin.education.models import Teacher, Course
from odin.education.factories import CourseFactory
from odin.competitions.models import Competition
from odin.competitions.factories import CompetitionFactory

from odin.common.faker import faker


class ProfileSignalTests(TestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    def test_create_user_creates_profile(self):
        profile_count = Profile.objects.count()
        BaseUserFactory()
        self.assertEqual(profile_count + 1, Profile.objects.count())

    def test_sign_up_request_creates_profile(self):
        url = self.reverse('account_signup')
        password = "1234asdf"
        data = {
            'email': faker.email(),
            'password1': password,
            'password2': password,
            'g-recaptcha-response': 'PASSED'
        }
        profile_count = Profile.objects.count()

        response = self.post(url_name=url, data=data, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(profile_count + 1, Profile.objects.count())


class SuperUserSignalTest(TestCase):
    def test_create_superuser_creates_teacher(self):
        teacher_count = Teacher.objects.count()
        BaseUser.objects.create_superuser(email=faker.email(), password=faker.password())
        self.assertEqual(teacher_count + 1, Teacher.objects.count())

    def test_create_superuser_adds_teacher_to_old_courses(self):
        CourseFactory.build_batch(5)
        user = BaseUser.objects.create_superuser(email=faker.email(), password=faker.password())
        user = user.teacher
        courses = Course.objects.all()
        for course in courses:
            self.assertIn(member=user, container=course.teachers.all())

    def test_create_superuser_adds_judge_to_competitions(self):
        CompetitionFactory.build_batch(5)
        user = BaseUser.objects.create_superuser(email=faker.email(), password=faker.password())
        competitions = Competition.objects.all()
        for competition in competitions:
            self.assertIn(user, competition.judges.all())
