from test_plus import TestCase
from django.test import Client

import jwt

from jwt.exceptions import InvalidSignatureError

from django.shortcuts import reverse

from odin.users.factories import BaseUserFactory

from odin.common.faker import faker

client = Client()


class TestJWTSecret(TestCase):
    def setUp(self):
        self.test_user_email = faker.email()
        self.test_password = faker.password()
        self.user = BaseUserFactory(email=self.test_user_email)
        self.user.set_password(self.test_password)
        self.user.is_active = True
        self.user.save()
        self.init_secret_key = self.user.secret_key
        self.login_url = reverse('api:auth:login')
        self.logout_url = reverse('api:auth:logout')
        self.user_detail_url = reverse('api:auth:user-detail')
        self.data = {
            'email': self.user.email,
            'password': self.test_password,
        }

    def test_user_can_decode_only_own_tokens(self):
        response1 = self.post(self.login_url, data=self.data)

        user = BaseUserFactory()
        user.is_active = True
        user.passwd = faker.password()
        user.set_password(user.passwd)
        user.save()

        data = {
            'email': user.email,
            'password': user.passwd,
        }

        response2 = self.post(self.login_url, data=data)

        token_user1 = response1.data['token']
        token_user2 = response2.data['token']

        self.assertNotEqual(token_user1, token_user2)
        self.assertNotEqual(self.user.secret_key, user.secret_key)

        with self.assertRaises(InvalidSignatureError):
            jwt.decode(token_user1, key=str(user.secret_key))

        with self.assertRaises(InvalidSignatureError):
            jwt.decode(token_user2, key=str(self.user.secret_key))

        self.assertEqual(
            self.user.email,
            jwt.decode(token_user1, key=str(self.user.secret_key))['email']
        )

        self.assertEqual(
            user.email,
            jwt.decode(token_user2, key=str(user.secret_key))['email']
        )

    def test_user_can_access_urls_with_token_only_after_login(self):
        self.response = self.post(self.login_url, data=self.data)

        token = self.response.data['token']

        response = client.get(self.user_detail_url, **{'HTTP_AUTHORIZATION': f'JWT {token}'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], self.user.email)

    def test_user_cannot_use_old_token_after_logout(self):
        self.response = self.post(self.login_url, data=self.data)
        token = self.response.data['token']

        # performs logout with jwt
        client.post(self.logout_url, **{'HTTP_AUTHORIZATION': f'JWT {token}'})

        response = client.get(self.user_detail_url, **{'HTTP_AUTHORIZATION': f'JWT {token}'})

        self.assertEqual(response.status_code, 401)

    def test_user_gets_new_user_secret_key_after_logout(self):
        self.response = self.post(self.login_url, data=self.data)
        token = self.response.data['token']

        # performs logout with jwt
        client.post(self.logout_url, **{'HTTP_AUTHORIZATION': f'JWT {token}'})

        self.user.refresh_from_db()

        self.assertNotEqual(self.init_secret_key, self.user.secret_key)
