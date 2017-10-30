from test_plus import TestCase

from django.utils import timezone

from ..templatetags.interview_extras import not_in_course, has_interviews_access

from odin.users.factories import BaseUserFactory, SuperUserFactory

from odin.applications.factories import ApplicationInfoFactory, ApplicationFactory
from odin.applications.models import Application

from odin.education.factories import CourseFactory
from odin.education.models import Student
from odin.education.services import add_student

from odin.interviews.models import Interviewer


class TestHasInterviewsAccess(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.user = BaseUserFactory()
        self.superuser = SuperUserFactory()
        self.interviewer = Interviewer.objects.create_from_user(self.user)
        self.app_info = ApplicationInfoFactory(course=self.course)
        self.interviewer.courses_to_interview.add(self.app_info)
        self.interviewer.save()

    def test_user_has_access_if_superuser(self):
        self.assertTrue(has_interviews_access(self.superuser))

    def test_user_has_access_if_interviewer_in_active_course(self):
        self.app_info.start_date = timezone.now() - timezone.timedelta(days=2)
        self.app_info.end_interview_date = timezone.now() + timezone.timedelta(days=1)
        self.app_info.save()
        self.assertTrue(has_interviews_access(self.interviewer))

    def test_user_does_not_have_access_if_interviewer_in_non_active_application_period(self):
        self.app_info.start_date = timezone.now() - timezone.timedelta(days=2)
        self.app_info.end_interview_date = timezone.now() - timezone.timedelta(days=1)
        self.app_info.save()
        self.assertFalse(has_interviews_access(self.interviewer))


class TestNotInCourse(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.app_info = ApplicationInfoFactory(course=self.course)
        self.user = BaseUserFactory()
        self.application = ApplicationFactory(user=self.user, application_info=self.app_info)

    def test_user_application_is_returned_if_user_is_not_student_in_course(self):
        qs = not_in_course(Application.objects.all(), self.course)
        self.assertEqual([self.application], list(qs))

    def test_user_application_is_not_returned_if_user_is_student_in_course(self):
        student = Student.objects.create_from_user(self.user)
        add_student(course=self.course, student=student)
        qs = not_in_course(Application.objects.all(), self.course)
        self.assertEqual([], list(qs))
