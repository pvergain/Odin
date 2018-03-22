from django.test import TestCase
from django.core.exceptions import ValidationError

from unittest.mock import patch

from odin.users.factories import BaseUserFactory
from odin.users.models import PasswordResetToken

from odin.authentication.services import initiate_reset_user_password


class InitiateResetUserPasswordTests(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()

    def test_inactive_user_cannot_initiate_password_reset(self):
        self.user.is_active = False
        self.user.save()

        with self.assertRaises(ValidationError):
            initiate_reset_user_password(user=self.user)

    @patch('odin.authentication.services.send_mail')
    def test_active_user_can_initiate_password_reset(self, mock_object):
        self.user.is_active = True
        self.user.save()

        token = initiate_reset_user_password(user=self.user)

        self.assertTrue(mock_object.called)
        self.assertEqual(isinstance(token, PasswordResetToken), True)
        self.assertIsNone(token.voided_at)
        self.assertIsNone(token.used_at)
