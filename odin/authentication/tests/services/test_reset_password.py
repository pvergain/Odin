from django.test import TestCase

from django.core.exceptions import ValidationError

from odin.users.factories import PasswordResetTokenFactory

from odin.authentication.services import reset_user_password

from odin.common.faker import faker


class ResetUserpasswordTests(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.token = PasswordResetTokenFactory()
        self.user = self.token.user
        self.user.set_password(self.test_password)
        self.user.save()
        self.initial_secret_key = self.user.secret_key
        self.password = faker.password()

    def test_user_cannot_reset_password_with_used_token(self):
        self.token.use()

        self.assertTrue(self.token.used)
        with self.assertRaises(ValidationError):
            reset_user_password(token=self.token,
                                password=self.password)

    def test_user_cannot_reset_password_with_voided_token(self):
        self.token.void()

        self.assertTrue(self.token.voided)
        with self.assertRaises(ValidationError):
            reset_user_password(token=self.token,
                                password=self.password)

    def test_user_can_reset_password_with_valid_token(self):
        user = reset_user_password(token=self.token,
                                   password=self.password)

        self.assertEqual(user, self.user)
        self.assertNotEqual(self.initial_secret_key, user.secret_key)
