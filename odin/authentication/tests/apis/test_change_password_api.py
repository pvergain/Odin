from test_plus import TestCase

from django.test import Client
from django.shortcuts import reverse

from unittest.mock import patch

from odin.users.factories import BaseUserFactory

from odin.common.faker import faker

import json

client = Client()


class TestUserChangePasswordApi(TestCase):
    def setUp(self):
        self.test_email = faker.email()
        self.test_password = faker.password()
        self.user = BaseUserFactory(email=self.test_email)
        self.user.set_password(self.test_password)
        self.user.save()
        self.login_url = reverse('api:auth:login')
        self.logout_url = reverse('api:auth:logout')
        self.change_password_url = reverse('api:auth:change-password')
        self.data = {
            'email': self.test_email,
            'password': self.test_password,
        }

    @patch('odin.authentication.apis.get_user_data')
    def test_logged_out_user_cannot_change_password(self, mock_object):
        mock_object.return_value = {}
        self.user.is_active = True
        self.user.save()

        # this should perform login
        login_response = client.post(self.login_url, data=self.data)

        token = login_response.data['token']

        # perform logout
        client.post(self.logout_url, **{'HTTP_AUTHORIZATION': f'JWT {token}'})

        data = {
            "old_password": self.test_password,
            "new_password": faker.password(),
        }

        # this should perform change password
        change_password_response = client.post(
            self.change_password_url,
            json.dumps(data),
            **{'HTTP_AUTHORIZATION': f'JWT {token}', 'content_type': 'application/json'},
        )

        self.assertEqual(change_password_response.status_code, 401)
        self.assertEqual(change_password_response.data['errors'][0]['code'], 'authentication_failed')

    @patch('odin.authentication.apis.get_user_data')
    def test_inactive_user_cannot_change_password(self, mock_object):
        mock_object.return_value = {}
        self.user.is_active = True
        self.user.save()

        # this should perform login
        login_response = client.post(self.login_url, data=self.data)

        token = login_response.data['token']

        self.user.is_active = False
        self.user.save()

        data = {
            'old_password': self.test_password,
            'new_password': faker.password(),
        }

        # this should perform change password
        change_password_response = client.post(
            self.change_password_url,
            json.dumps(data),
            **{'HTTP_AUTHORIZATION': f'JWT {token}', 'content_type': 'application/json'},
        )

        self.assertEqual(change_password_response.status_code, 401)
        self.assertEqual(change_password_response.data['errors'][0]['message'], 'User account is disabled.')

    @patch('odin.authentication.apis.get_user_data')
    def test_user_cannot_change_password_with_invalid_token(self, mock_object):
        mock_object.return_value = {}
        self.user.is_active = True
        self.user.save()

        # this should perform login
        login_response = client.post(self.login_url, data=self.data)

        token = login_response.data['token']

        self.user.rotate_secret_key()

        data = {
            'old_password': self.test_password,
            'new_password': faker.password(),
        }

        # this should perform change password
        change_password_response = client.post(
            self.change_password_url,
            json.dumps(data),
            **{'HTTP_AUTHORIZATION': f'JWT {token}', 'content_type': 'application/json'},
        )

        self.assertEqual(change_password_response.status_code, 401)
        self.assertEqual(change_password_response.data['errors'][0]['code'], 'authentication_failed')

    @patch('odin.authentication.apis.get_user_data')
    def test_user_cannot_change_password_with_wrong_old_password(self, mock_object):
        mock_object.return_value = {}
        self.user.is_active = True
        self.user.save()

        # this should perform login
        login_response = client.post(self.login_url, data=self.data)

        token = login_response.data['token']

        data = {
            "old_password": faker.password(),
            "new_password": faker.password(),
        }

        # this should perform change password
        change_password_response = client.post(
            self.change_password_url,
            json.dumps(data),
            **{'HTTP_AUTHORIZATION': f'JWT {token}', 'content_type': 'application/json'},
        )

        self.assertEqual(change_password_response.status_code, 400)
        self.assertEqual(change_password_response.data['errors'][0]['message'], 'Old password is invalid.')

    @patch('odin.authentication.apis.change_user_password')
    @patch('odin.authentication.apis.get_user_data')
    def test_active_user_can_change_password_with_valid_token(self, mock1, mock2):
        mock1.return_value = {}
        self.user.is_active = True
        self.user.save()

        # this should perform login
        login_response = client.post(self.login_url, data=self.data)

        token = login_response.data['token']

        data = {
            "old_password": self.test_password,
            "new_password": faker.password(),
        }

        # this should perform change password
        change_password_response = client.post(
            self.change_password_url,
            json.dumps(data),
            **{'HTTP_AUTHORIZATION': f'JWT {token}', 'content_type': 'application/json'},
        )

        self.assertTrue(mock2.called)
        self.assertEqual(change_password_response.status_code, 202)
