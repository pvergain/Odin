from test_plus import TestCase

from dateutil import parser
from datetime import timedelta

from django.core.exceptions import ValidationError

from ..services import create_course
from ..models import Course, Week
from ..factories import CourseFactory

from odin.common.faker import faker


class TestCreateCourse(TestCase):

    def test_course_is_created_successfully_with_valid_data(self):
        start_date = parser.parse(faker.date())
        self.assertEqual(0, Course.objects.count())
        data = {
            'name': faker.word(),
            'start_date': start_date,
            'end_date': start_date + timedelta(days=faker.pyint()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
        }
        create_course(**data)
        self.assertEqual(1, Course.objects.count())

    def test_create_course_raises_error_on_duplicate_name(self):
        start_date = parser.parse(faker.date())
        course = CourseFactory()
        self.assertEqual(1, Course.objects.count())
        data = {
            'name': course.name,
            'start_date': start_date,
            'end_date': start_date + timedelta(days=faker.pyint()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
        }
        with self.assertRaises(ValidationError):
            create_course(**data)
        self.assertEqual(1, Course.objects.count())

    def test_create_course_creates_weeks_for_course_successfully(self):
        start_date = parser.parse(faker.date())
        self.assertEqual(0, Course.objects.count())
        data = {
            'name': faker.word(),
            'start_date': start_date,
            'end_date': start_date + timedelta(days=faker.pyint()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
        }
        course = create_course(**data)
        weeks = course.duration_in_weeks
        self.assertEqual(1, Course.objects.count())
        self.assertEqual(weeks, Week.objects.count())

    def test_create_course_starts_week_from_monday(self):
        start_date = parser.parse(faker.date())
        data = {
            'name': faker.word(),
            'start_date': start_date,
            'end_date': start_date + timedelta(days=faker.pyint()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
        }
        course = create_course(**data)
        weeks = course.duration_in_weeks
        self.assertEqual(1, Course.objects.count())
        self.assertEqual(weeks, Week.objects.count())
        week_one = Week.objects.first()
        self.assertEqual(0, week_one.start_date.weekday())
