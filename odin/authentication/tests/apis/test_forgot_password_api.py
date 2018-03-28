from test_plus import TestCase

from django.shortcuts import reverse

from unittest.mock import patch

from odin.common.faker import faker

from odin.users.factories import BaseUserFactory


class ForgotPasswordAPiTests(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()
        self.unknown_user_email = faker.email()
        self.url = reverse('api:auth:forgot-password-reset')
        self.data = {
            'user': self.user.email
        }

    def test_unknown_user_cannot_initiate_password_reset(self):
        data = {
            'user': self.unknown_user_email
        }

        response = self.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)

    def test_inactive_user_cannot_initiate_password_reset(self):
        response = self.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 400)

    @patch('odin.authentication.apis.initiate_reset_user_password')
    def test_active_user_can_initiate_password_reset(self, mock_object):
        self.user.is_active = True
        self.user.save()

        response = self.post(self.url, data=self.data)
        self.assertTrue(mock_object.called)
        self.assertEqual(response.status_code, 202)
