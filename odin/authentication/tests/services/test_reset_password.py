from django.test import TestCase

from django.core.exceptions import ValidationError

from odin.users.models import PasswordResetToken

from odin.users.factories import BaseUserFactory

from odin.authentication.services import reset_user_password

from faker import Faker
fake = Faker()


class ResetUserpasswordTest(TestCase):
    def setUp(self):
        self.test_password = fake.password()
        self.user = BaseUserFactory()
        self.user.set_password(self.test_password)
        self.user.save()
        self.initial_secret_key = self.user.secret_key
        self.token = PasswordResetToken()
        self.token.user = self.user
        self.token.save()

    def test_user_cannot_reset_password_with_used_token(self):
        password = fake.password()
        self.token.use()

        with self.assertRaises(ValidationError):
            reset_user_password(token=self.token,
                                password=password)

    def test_user_cannot_reset_password_with_voided_token(self):
        password = fake.password()
        self.token.void()

        with self.assertRaises(ValidationError):
            reset_user_password(token=self.token,
                                password=password)

    def test_user_can_reset_password_with_valid_token(self):
        password = fake.password()

        user = reset_user_password(token=self.token,
                                   password=password)

        self.assertEqual(user, self.user)
        self.assertNotEqual(self.initial_secret_key, user.secret_key)
