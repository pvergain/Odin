from test_plus import TestCase

from django.core.exceptions import ValidationError

from odin.users.factories import BaseUserFactory
from odin.education.factories import CourseFactory
from odin.applications.factories import ApplicationInfoFactory
from odin.interviews.services import add_course_to_interviewer_courses
from odin.interviews.factories import InterviewerFactory
from odin.applications.factories import ApplicationFactory

from ..services import create_new_interview_for_application, create_interviewer_free_time
from ..factories import InterviewFactory, InterviewerFreeTimeFactory
from ..models import Interviewer


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


class TestCreateNewInterviewForApplication(TestCase):
    def setUp(self):
        self.application = ApplicationFactory()
        self.interview = InterviewFactory(application=self.application)

    def test_create_new_interview_raises_validation_error_when_chosen_interview_already_has_an_application(self):
        self.new_interview = InterviewFactory(application=self.application)

        with self.assertRaises(ValidationError):
            create_new_interview_for_application(application=self.application,
                                                 uuid=self.new_interview.uuid)

    def test_create_new_interview_creates_new_interview_when_chosen_interview_is_free(self):
        self.new_interview = InterviewFactory(application=None)
        create_new_interview_for_application(application=self.application,
                                             uuid=self.new_interview.uuid)

        self.new_interview.refresh_from_db()
        self.assertEqual(self.new_interview.application, self.application)


class TestCreateInterviewFreeTimeSlot(TestCase):
    def setUp(self):
        self.interviewer = Interviewer.objects.create_from_user(BaseUserFactory())
        self.slot = InterviewerFreeTimeFactory(interviewer=self.interviewer)

    def test_create_instance_with_overlapping_time_interval_for_same_interviewer_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            create_interviewer_free_time(interviewer=self.interviewer,
                                         date=self.slot.date,
                                         start_time=self.slot.start_time,
                                         end_time=self.slot.end_time,
                                         interview_time_length=20,
                                         break_time=5)
