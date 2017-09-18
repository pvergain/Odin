from odin.common.faker import faker

from test_plus import TestCase
from django.test.utils import override_settings
from unittest.mock import patch
from unittest import skip

from allauth.account.models import EmailAddress

from odin.users.models import BaseUser

from odin.users.factories import BaseUserFactory

import os


class AuthorizationTests(TestCase):
    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    @skip("Temporary for competition")
    def test_user_registration_with_recaptcha_passed(self):
        user_count = BaseUser.objects.count()
        url = self.reverse('account_signup')
        password = faker.password()
        data = {
            'email': faker.email(),
            'password1': password,
            'g-recaptcha-response': 'PASSED'
        }
        response = self.post(url_name=url, data=data, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user_count + 1, BaseUser.objects.count())

    @skip("Temporary for competition")
    def test_user_registration_with_recaptcha_not_passed(self):
        user_count = BaseUser.objects.count()
        url = self.reverse('account_signup')
        password = faker.password()
        data = {
            'email': faker.email(),
            'password1': password,
        }
        response = self.post(url_name=url, data=data, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_count, BaseUser.objects.count())

    @skip("Temporary for competition")
    def test_user_registration_for_already_logged_in_user(self):
        test_password = faker.password()
        user = BaseUserFactory(password=test_password)
        user.is_active = True
        user.save()
        user_count = BaseUser.objects.count()
        with self.login(email=user.email, password=test_password):
            url = self.reverse('account_signup')
            response = self.get(url_name=url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(user_count, BaseUser.objects.count())


class EmailBackendTests(TestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    @skip("Temporary for competition")
    @override_settings(USE_DJANGO_EMAIL_BACKEND=False)
    @patch('odin.common.tasks.send_template_mail.delay')
    def test_sends_mail_to_address_from_post_to_account_signup(self, mock_send_mail):
        test_password = faker.password()
        test_email = faker.email()
        url = self.reverse('account_signup')
        data = {
            'email': test_email,
            'password1': test_password,
            'g-recaptcha-response': 'PASSED'
        }
        self.post(url_name=url, data=data)
        self.assertEqual(mock_send_mail.called, True)
        (template_name, recipients, context), kwargs = mock_send_mail.call_args
        self.assertEqual([test_email], recipients)

    @override_settings(USE_DJANGO_EMAIL_BACKEND=False)
    @patch('odin.common.tasks.send_template_mail.delay')
    def test_sends_mail_to_address_from_post_on_password_reset(self, mock_send_mail):
        test_password = faker.password()
        user = BaseUserFactory(email=faker.email(), password=test_password)
        user.is_active = True
        user.save()
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=True,
            primary=True
        )
        url = self.reverse('account_reset_password')
        data = {'email': user.email}
        self.post(url_name=url, data=data)
        self.assertEqual(mock_send_mail.called, True)
        (template_name, recipients, context), kwargs = mock_send_mail.call_args
        self.assertEqual([user.email], recipients)
