from django.test import TestCase

from django.core.exceptions import ValidationError

from odin.users.factories import BaseUserFactory
from odin.authentication.services import change_user_password

from odin.common.faker import faker


class TestChangeUserPassword(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory()
        self.user.set_password(self.test_password)
        self.user.is_active = True
        self.user.save()
        self.init_secret_key = self.user.secret_key

    def test_user_cannot_change_password_with_wrong_old_password(self):

        with self.assertRaises(ValidationError):
            change_user_password(
                user=self.user,
                old_password=faker.password(),
                new_password=faker.password()
            )

    def test_user_cannot_change_password_with_empty_old_password(self):
        with self.assertRaises(ValidationError):
            change_user_password(
                user=self.user,
                old_password='',
                new_password=faker.password()
            )

    def test_user_cannot_change_password_with_empty_new_password(self):
        with self.assertRaises(ValidationError):
            change_user_password(
                user=self.user,
                old_password=self.test_password,
                new_password=''
            )

    def test_user_cannot_change_password_if_account_is_inactive(self):
        self.user.is_active = False
        self.user.save()

        with self.assertRaises(ValidationError):
            change_user_password(
                user=self.user,
                old_password=self.test_password,
                new_password=faker.password()
            )

    def test_user_can_change_password_with_valid_old_and_new_password_when_active(self):

        new_password = faker.password()

        change_user_password(
            user=self.user,
            old_password=self.test_password,
            new_password=new_password,
        )

        self.user.refresh_from_db()

        self.assertNotEqual(self.init_secret_key, self.user.secret_key)
        self.assertTrue(self.user.check_password(new_password))
