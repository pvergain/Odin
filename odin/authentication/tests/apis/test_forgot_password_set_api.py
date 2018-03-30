from test_plus import TestCase

from django.shortcuts import reverse

from unittest.mock import patch

from odin.users.factories import PasswordResetTokenFactory

from odin.common.faker import faker


class ForgotPasswordSetApiTest(TestCase):
    def setUp(self):
        self.password_reset_token = PasswordResetTokenFactory()
        self.user = self.password_reset_token.user
        self.user.is_active = True
        self.user.save()
        self.url = reverse('api:auth:forgot-password-set')
        self.password = faker.password()
        self.data = {
            'token': str(self.password_reset_token.token),
            'password': self.password,
        }

    def test_cannot_reset_password_with_voided_token(self):
        self.password_reset_token.void()

        response = self.post(self.url, data=self.data)

        self.assertTrue(self.password_reset_token.voided)
        self.assertEqual(response.status_code, 400)

    def test_cannot_reset_password_with_used_token(self):
        self.password_reset_token.use()

        response = self.post(self.url, data=self.data)
        self.assertTrue(self.password_reset_token.used)
        self.assertEqual(response.status_code, 400)

    @patch('odin.authentication.apis.reset_user_password')
    def test_can_reset_password_with_valid_token(self, mock_object):

        response = self.post(self.url, data=self.data)

        self.assertTrue(mock_object.called)
        self.assertEqual(response.status_code, 202)
