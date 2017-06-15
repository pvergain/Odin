from test_plus import TestCase

from allauth.account.models import EmailAddress

from ..factories import BaseUserFactory
from ...common.faker import faker

import os


class TestLogInView(TestCase):
    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.test_password = faker.password()
        self.url = self.reverse('account_login')

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    def test_readable_errors_are_empty_on_get(self):
        response = self.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertInContext('readable_errors')
        self.assertEqual(0, len(response.context['readable_errors']))

    def test_readable_errors_are_not_None_when_form_invalid(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.save()
        data = {
            'login': user.email,
            'password': 'wrong_password'
        }
        response = self.post(url_name=self.url, data=data, follow=False)

        self.assertInContext('readable_errors')
        self.assertNotEqual(0, len(response.context['readable_errors']))

    def test_view_redirects_to_confirmation_prompt_when_email_not_confirmed(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.save()
        data = {
            'login': user.email,
            'password': self.test_password
        }
        response = self.post(url_name=self.url, data=data, follow=True)

        self.assertRedirects(response=response, expected_url=self.reverse('account_email_verification_sent'))

    def test_view_redirects_to_profile_on_post_when_email_is_confirmed(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        email = EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
        email.save()
        user.emailaddress_set.add(email)
        user.emailaddress_set.first().verified = True
        user.save()
        data = {
            'login': user.email,
            'password': self.test_password
        }
        response = self.post(url_name=self.url, data=data, follow=True)

        self.assertRedirects(response=response, expected_url=self.reverse('education:profile'))


class TestSignUpView(TestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.test_password = faker.password()
        self.url = self.reverse('account_signup')

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    def test_readable_errors_are_empty_on_get(self):
        response = self.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertInContext('readable_errors')
        self.assertEqual(0, len(response.context['readable_errors']))

    def test_readable_errors_are_not_None_when_form_invalid(self):
        data = {
            'email': faker.email(),
            'password1': self.test_password
        }
        response = self.post(url_name=self.url, data=data, follow=False)

        self.assertInContext('readable_errors')
        self.assertNotEqual(0, len(response.context['readable_errors']))

    def test_view_redirects_to_confirmation_prompt_upon_success(self):
        data = {
            'email': faker.email(),
            'password1': self.test_password,
            'g-recaptcha-response': 'PASSED'
        }
        response = self.post(url_name=self.url, data=data, follow=True)

        self.assertRedirects(response=response, expected_url=self.reverse('account_email_verification_sent'))


class TestPasswordResetView(TestCase):

    def setUp(self):
        self.email = "alabala@alabala.com"
        self.user = BaseUserFactory(email=self.email)
        self.url = self.reverse('account_reset_password')

    def test_readable_errors_are_empty_on_get(self):
        response = self.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertInContext('readable_errors')
        self.assertEqual(0, len(response.context['readable_errors']))

    def test_view_redirects_to_confirmation_prompt_upon_success(self):
        data = {
            'email': "alabala@alabala.com"
        }
        response = self.post(url_name=self.url, data=data, follow=True)

        self.assertRedirects(response=response, expected_url=self.reverse('account_reset_password_done'))
