from datetime import timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError

from odin.common.utils import get_now

from odin.education.factories import CourseFactory
from odin.education.models import Course


class CourseTests(TestCase):
    def test_course_end_date_cannot_be_before_start_date(self):
        start_date = get_now()
        end_date = get_now() - timedelta(days=1)

        course_data = CourseFactory.build()
        course_data['start_date'] = start_date
        course_data['end_date'] = end_date

        course = Course(**course_data)

        with self.assertRaises(ValidationError):
            course.full_clean()
