from test_plus import TestCase

from django.contrib.messages.storage.base import Message

from odin.common.faker import faker
from odin.common.templatetags.common_extras import get_message


class TestGetMessage(TestCase):
    def test_get_message_removes_parentheses(self):
        word1 = faker.word()
        word2 = faker.word()
        message = Message(level=1, message=f'[{word2}, {word1}]')
        self.assertEqual(f'{word2}, {word1}', get_message(message))
