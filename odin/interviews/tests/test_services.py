from test_plus import TestCase

from django.core.exceptions import ValidationError

from odin.education.factories import CourseFactory
from odin.applications.factories import ApplicationInfoFactory
from odin.interviews.services import add_course_to_interviewer_courses
from odin.interviews.factories import InterviewerFactory


class TestAddCourseToInterViewerCourses(TestCase):
    def setUp(self):
        self.interviewer = InterviewerFactory()
        self.course = CourseFactory()

    def test_service_raises_validation_error_when_course_does_not_have_app_info(self):
        with self.assertRaises(ValidationError):
            add_course_to_interviewer_courses(interviewer=self.interviewer, course=self.course)

    def test_service_adds_course_to_interviewer_courses_when_course_has_app_info(self):
        current_course_count = self.interviewer.courses_to_interview.count()
        ApplicationInfoFactory(course=self.course)
        self.course.refresh_from_db()
        add_course_to_interviewer_courses(interviewer=self.interviewer, course=self.course)

        self.assertEqual(current_course_count + 1, self.interviewer.courses_to_interview.count())
