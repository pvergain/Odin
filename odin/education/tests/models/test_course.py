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

    def test_course_has_started_if_start_date_is_in_the_past(self):
        start_date = (get_now() - timedelta(days=1)).date()
        end_date = (get_now() + timedelta(days=1)).date()

        course_data = CourseFactory.build()
        course_data['start_date'] = start_date
        course_data['end_date'] = end_date

        course = Course(**course_data)

        self.assertTrue(course.has_started)

    def test_course_has_started_if_start_date_is_today(self):
        start_date = get_now().date()
        end_date = (get_now() + timedelta(days=1)).date()

        course_data = CourseFactory.build()
        course_data['start_date'] = start_date
        course_data['end_date'] = end_date

        course = Course(**course_data)

        self.assertTrue(course.has_started)

    def test_course_has_not_started_if_start_date_is_in_the_future(self):
        start_date = (get_now() + timedelta(days=1)).date()
        end_date = (get_now() + timedelta(days=2)).date()

        course_data = CourseFactory.build()
        course_data['start_date'] = start_date
        course_data['end_date'] = end_date

        course = Course(**course_data)

        self.assertFalse(course.has_started)

    def test_course_has_finished_with_end_date_today(self):
        start_date = (get_now() - timedelta(days=1)).date()
        end_date = get_now().date()

        course_data = CourseFactory.build()
        course_data['start_date'] = start_date
        course_data['end_date'] = end_date

        course = Course(**course_data)

        self.assertTrue(course.has_finished)

    def test_course_has_finished_with_end_date_bigger_than_today(self):
        start_date = (get_now() + timedelta(days=1)).date()
        end_date = (get_now() + timedelta(days=2)).date()

        course_data = CourseFactory.build()
        course_data['start_date'] = start_date
        course_data['end_date'] = end_date

        course = Course(**course_data)

        self.assertFalse(course.has_finished)

    def test_can_generate_certificates_with_end_date_in_time_gap(self):
        start_date = (get_now() + timedelta(days=1)).date()
        end_date = (get_now() + timedelta(days=2)).date()

        course_data = CourseFactory.build()
        course_data['start_date'] = start_date
        course_data['end_date'] = end_date

        course = Course(**course_data)

        self.assertTrue(course.can_generate_certificates)

    def test_can_generate_certificates_with_end_date_outside_time_gap(self):
        start_date = (get_now() - timedelta(days=30)).date()
        end_date = (get_now() - timedelta(days=16)).date()

        course_data = CourseFactory.build()
        course_data['start_date'] = start_date
        course_data['end_date'] = end_date

        course = Course(**course_data)

        self.assertFalse(course.can_generate_certificates)

    def test_duration_in_weeks_should_return_two(self):
        start_date = get_now().date()
        end_date = (get_now() + timedelta(days=13)).date()

        course_data = CourseFactory.build()
        course_data['start_date'] = start_date
        course_data['end_date'] = end_date

        course = Course(**course_data)

        self.assertEqual(2, course.duration_in_weeks)

    def test_duration_in_weeks_should_return_three(self):
        start_date = get_now().date()
        end_date = (get_now() + timedelta(days=14)).date()

        course_data = CourseFactory.build()
        course_data['start_date'] = start_date
        course_data['end_date'] = end_date

        course = Course(**course_data)

        self.assertEqual(3, course.duration_in_weeks)
