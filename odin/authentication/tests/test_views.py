import os

from test_plus import TestCase

from django.core import mail

from allauth.account.models import EmailAddress

from odin.users.factories import BaseUserFactory
from odin.common.faker import faker


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

    def test_readable_errors_are_not_none_when_form_is_invalid(self):
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

    def test_view_redirects_to_confirmation_prompt_when_email_is_not_confirmed(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.save()
        data = {
            'login': user.email,
            'password': self.test_password
        }
        response = self.post(url_name=self.url, data=data, follow=True)

        self.assertRedirects(response=response,
                             expected_url=self.reverse('account_email_verification_sent'))

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

        self.assertRedirects(response=response, expected_url=self.reverse('dashboard:users:profile'))


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

    def test_readable_errors_are_not_none_when_form_is_invalid(self):
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
        self.email = faker.email()
        self.user = BaseUserFactory(email=self.email)
        self.url = self.reverse('account_reset_password')

    def test_readable_errors_are_empty_on_get(self):
        response = self.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertInContext('readable_errors')
        self.assertEqual(0, len(response.context['readable_errors']))

    def test_view_redirects_to_confirmation_prompt_upon_success(self):
        data = {
            'email': self.email
        }
        response = self.post(url_name=self.url, data=data, follow=True)

        self.assertRedirects(response=response, expected_url=self.reverse('account_reset_password_done'))

    def test_readable_errors_are_not_empty_when_form_is_invalid(self):
        data = {
            'email': faker.email()
        }
        response = self.post(url_name=self.url, data=data, follow=False)

        self.assertInContext('readable_errors')
        self.assertNotEqual(0, len(response.context['readable_errors']))


class TestPasswordResetFromKeyView(TestCase):
    def setUp(self):
        self.email = faker.email()
        self.user = BaseUserFactory(email=self.email)

    def test_readable_errors_are_empty_on_get(self):
        data = {
            'email': self.email
        }

        url = self.reverse('account_reset_password')
        response = self.post(url_name=url, data=data, follow=True)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.email])

        body = mail.outbox[0].body
        url = '/auth' + body[body.find('/password/reset/'):].split()[0]
        response = self.get(url)

        self.assertEqual(200, response.status_code)
        self.assertInContext('readable_errors')
        self.assertEqual(0, len(response.context['readable_errors']))

    def test_readable_errors_are_not_empty_when_form_is_invalid(self):
        data = {
            'email': self.email
        }

        url = self.reverse('account_reset_password')
        response = self.post(url_name=url, data=data, follow=True)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.email])

        body = mail.outbox[0].body
        url = '/auth' + body[body.find('/password/reset/'):].split()[0]
        response = self.get(url)

        self.assertEqual(200, response.status_code)

        data = {
            'password1': "ivan"
        }

        response = self.post(url_name=url, data=data, follow=False)

        self.assertInContext('readable_errors')
        self.assertNotEqual(0, len(response.context['readable_errors']))

    def test_view_redirects_to_login_prompt_upon_success(self):
        data = {
            'email': self.email
        }

        url = self.reverse('account_reset_password')
        response = self.post(url_name=url, data=data, follow=True)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.email])

        body = mail.outbox[0].body
        url = '/auth' + body[body.find('/password/reset/'):].split()[0]
        response = self.get(url)

        self.assertEqual(200, response.status_code)

        data = {
            'password1': faker.password()
        }

        response = self.post(url_name=url, data=data, follow=True)

        self.assertRedirects(response=response, expected_url=self.reverse('account_login'))
