from test_plus import TestCase

from odin.education.models import Student
from odin.users.factories import BaseUserFactory
from rest_framework_jwt.utils import jwt_decode_handler as decode


class TestUserSercetChange(TestCase):
    def setUp(self):
        user = BaseUserFactory()
        student = Student.objects.create_from_user(user)
        student.save()

    def test_user_can_decode_only_own_tokens(self):
        '''
        TO DO:
            user default user and login and get token
            create second user. login and get token
            1. try user1 to decode user 2 token
            2. try user2 decode user1 token 
            assert corectness
        '''

        pass