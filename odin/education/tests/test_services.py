from test_plus import TestCase

from dateutil import parser

from django.core.exceptions import ValidationError

from ..services import create_course
from ..models import Course, Week
from ..factories import CourseFactory

from odin.common.faker import faker


class TestCreateCourse(TestCase):

    def test_course_is_created_successfully_with_valid_data(self):
        self.assertEqual(0, Course.objects.count())
        data = {
            'name': faker.word(),
            'start_date': parser.parse(faker.date()),
            'end_date': parser.parse(faker.date()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
        }
        create_course(**data)
        self.assertEqual(1, Course.objects.count())

    def test_create_course_raises_error_on_duplicate_name(self):
        course = CourseFactory()
        self.assertEqual(1, Course.objects.count())
        data = {
            'name': course.name,
            'start_date': parser.parse(faker.date()),
            'end_date': parser.parse(faker.date()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
        }
        with self.assertRaises(ValidationError):
            create_course(**data)
        self.assertEqual(1, Course.objects.count())

    def test_create_course_creates_weeks_for_course_successfully(self):
        self.assertEqual(0, Course.objects.count())
        data = {
            'name': faker.word(),
            'start_date': parser.parse(faker.date()),
            'end_date': parser.parse(faker.date()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
        }
        course = create_course(**data)
        weeks = course.duration_in_weeks
        self.assertEqual(1, Course.objects.count())
        self.assertEqual(weeks, Week.objects.count())
