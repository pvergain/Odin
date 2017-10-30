from test_plus import TestCase

from django.core.exceptions import ValidationError
from django.utils import timezone

from odin.users.factories import BaseUserFactory
from odin.education.factories import CourseFactory
from odin.applications.factories import ApplicationInfoFactory
from odin.interviews.services import add_course_to_interviewer_courses, assign_accepted_users_to_courses
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


class TestAssignAcceptedUsersToCourses(TestCase):
    def setUp(self):
        start_date = timezone.now().date() - timezone.timedelta(days=3)
        end_date = timezone.now().date() + timezone.timedelta(days=5)
        start_interview_date = timezone.now().date() - timezone.timedelta(days=2)
        end_interview_date = timezone.now().date() + timezone.timedelta(days=4)
        self.application_info = ApplicationInfoFactory(
            start_date=start_date,
            end_date=end_date,
            start_interview_date=start_interview_date,
            end_interview_date=end_interview_date
        )
        self.application = ApplicationFactory(application_info=self.application_info)

    def test_task_assigns_users_with_accepted_applications_to_courses(self):
        self.application.is_accepted = True
        self.application.save()

        course_student_count = self.application_info.course.students.count()
        assign_accepted_users_to_courses()
        self.application_info.course.refresh_from_db()
        self.assertEqual(course_student_count + 1, self.application_info.course.students.count())

    def test_task_does_not_assign_user_with_not_accepted_application(self):
        self.application.is_accepted = False
        self.application.save()

        course_student_count = self.application_info.course.students.count()
        assign_accepted_users_to_courses()
        self.application_info.course.refresh_from_db()
        self.assertEqual(course_student_count, self.application_info.course.students.count())
