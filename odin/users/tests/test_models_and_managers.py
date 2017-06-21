from test_plus import TestCase

from django.core.exceptions import ValidationError

from ..models import BaseUser, Profile

from odin.common.faker import faker


class BaseUserTests(TestCase):
    def setUp(self):
        self.email = faker.email()
        self.test_password = faker.password()

    def test_create_user_creates_single_user(self):
        self.assertEqual(0, BaseUser.objects.count())
        BaseUser.objects.create_user(email=self.email, password=self.test_password)
        self.assertEqual(1, BaseUser.objects.count())

    def test_create_user_raises_validation_error_when_email_invalid(self):
        with self.assertRaises(ValidationError):
            BaseUser.objects.create_user(email='invalid email', password=self.test_password)

    def test_create_user_raises_validation_error_when_user_already_exists(self):
        BaseUser.objects.create(email=self.email, password=self.test_password)
        with self.assertRaises(ValidationError):
            BaseUser.objects.create_user(email=self.email, password=self.test_password)

    def test_create_user_raises_value_error_when_no_email_is_provided(self):
        with self.assertRaises(ValueError):
            BaseUser.objects.create_user(email=None, password=self.test_password)


class ProfileTests(TestCase):

    def setUp(self):
        self.email = faker.email()
        self.test_password = faker.password()

    def test_there_is_no_github_url_if_not_signed_up_with_github(self):
        self.assertEqual(0, Profile.objects.count())
        user = BaseUser.objects.create(email=self.email, password=self.test_password)
        self.assertEqual(1, Profile.objects.count())
        profile = user.profile
        self.assertIsNone(profile.get_gh_profile_url())
