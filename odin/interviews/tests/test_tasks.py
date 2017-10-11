from test_plus import TestCase

from django.utils import timezone

from odin.applications.factories import ApplicationInfoFactory, ApplicationFactory

from ..tasks import assign_accepted_users_to_courses


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
