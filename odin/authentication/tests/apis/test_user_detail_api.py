from test_plus import TestCase

from odin.common.faker import faker

from django.test import Client
from django.shortcuts import reverse

from unittest.mock import patch

from odin.users.factories import BaseUserFactory

client = Client()


class TestUserDetailApi(TestCase):
    def setUp(self):
        self.test_email = faker.email()
        self.test_password = faker.password()
        self.user = BaseUserFactory(email=self.test_email)
        self.user.set_password(self.test_password)
        self.user.is_active = True
        self.user.save()
        self.login_url = reverse('api:auth:login')
        self.user_detail_url = reverse('api:auth:user-detail')
        self.data = {
            'email': self.test_email,
            'password': self.test_password,
        }

    @patch('odin.authentication.apis.get_user_data')
    def test_cannot_fetch_user_data_with_invalid_token(self, mock_object):
        mock_object.return_value = {}

        # perform login
        login_response = client.post(self.login_url, data=self.data)

        token = login_response.data['token']

        # that should invalidate all previously aquired tokens
        self.user.rotate_secret_key()

        me_response = client.get(self.user_detail_url, **{'HTTP_AUTHORIZATION': f'JWT {token}'})

        self.assertTrue(mock_object.called)
        self.assertEqual(me_response.status_code, 401)
        self.assertEqual(me_response.data['errors'][0]['code'], 'authentication_failed')

    @patch('odin.authentication.apis.get_user_data')
    def test_can_fetch_use_data_with_valid_token(self, mock_object):
        mock_object.return_value = {}
        # perform login
        login_response = client.post(self.login_url, data=self.data)

        token = login_response.data['token']

        me_response = client.get(self.user_detail_url, **{'HTTP_AUTHORIZATION': f'JWT {token}'})

        self.assertTrue(mock_object.called)
        self.assertEqual(me_response.status_code, 200)
