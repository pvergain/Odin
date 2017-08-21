from test_plus import TestCase

from django.utils import timezone

from odin.common.faker import faker
from odin.users.factories import ProfileFactory

from ..factories import CheckInFactory, StudentFactory, LectureFactory, CourseFactory
from ..services import add_student
from ..tasks import calculate_presence
from ..models import CheckIn


class TestCalculatePresenceTask(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.student = StudentFactory(password=self.test_password)
        self.other_student = StudentFactory(password=self.test_password)
        self.profile = ProfileFactory(user=self.student.user)
        self.other_profile = ProfileFactory(user=self.other_student.user)
        self.student.is_active = self.other_student.is_active = True
        self.student.save()
        self.other_student.save()

        self.course = CourseFactory(start_date=timezone.now().date() - timezone.timedelta(days=10),
                                    end_date=timezone.now().date() + timezone.timedelta(days=10))
        self.course_assignment = add_student(self.course, self.student)
        self.other_course_assignment = add_student(self.course, self.other_student)

        LectureFactory(course=self.course, date=timezone.now().date() - timezone.timedelta(days=9))
        LectureFactory(course=self.course, date=timezone.now().date() - timezone.timedelta(days=7))
        LectureFactory(course=self.course, date=timezone.now().date() - timezone.timedelta(days=5))
        LectureFactory(course=self.course, date=timezone.now().date() - timezone.timedelta(days=3))

    def test_calculate_presence_when_student_has_no_check_ins_for_course(self):
        self.assertEqual(self.course_assignment.student_presence, 0)
        self.assertEqual(self.other_course_assignment.student_presence, 0)

        calculate_presence()

        self.assertEqual(self.course_assignment.student_presence, 0)
        self.assertEqual(self.other_course_assignment.student_presence, 0)

    def test_calculate_presence_when_student_has_checkins_for_other_dates(self):
        CheckInFactory(mac=self.profile.mac,
                       user=self.student.user,
                       date=timezone.now().date() - timezone.timedelta(days=8))
        CheckInFactory(mac=self.profile.mac,
                       user=self.student.user,
                       date=timezone.now().date() - timezone.timedelta(days=6))

        self.assertEqual(self.course_assignment.student_presence, 0)

        calculate_presence()

        self.assertEqual(self.course_assignment.student_presence, 0)

    def test_calculate_presence_when_student_has_checkins_for_course_lectures(self):
        CheckInFactory(mac=self.profile.mac,
                       user=self.student.user,
                       date=timezone.now().date() - timezone.timedelta(days=9))
        CheckInFactory(mac=self.profile.mac,
                       user=self.student.user,
                       date=timezone.now().date() - timezone.timedelta(days=7))
        CheckInFactory(mac=self.profile.mac,
                       user=self.student.user,
                       date=timezone.now().date() - timezone.timedelta(days=5))
        CheckInFactory(mac=self.profile.mac,
                       user=self.student.user,
                       date=timezone.now().date() - timezone.timedelta(days=3))
        CheckInFactory(mac=self.other_profile.mac,
                       user=self.other_student.user,
                       date=timezone.now().date() - timezone.timedelta(days=7))

        self.assertEqual(self.course_assignment.student_presence, 0)
        self.assertEqual(self.other_course_assignment.student_presence, 0)

        self.assertEqual(4, CheckIn.objects.get_user_dates(user=self.student.user, course=self.course).count())
        self.assertEqual(1, CheckIn.objects.get_user_dates(user=self.other_student.user, course=self.course).count())

        calculate_presence()

        self.course_assignment.refresh_from_db()
        self.assertEqual(self.course_assignment.student_presence, 100)

        self.other_course_assignment.refresh_from_db()
        self.assertEqual(self.other_course_assignment.student_presence, 25)

    def test_calculate_presence_when_student_has_changed_mac_address_at_some_point(self):
        CheckInFactory(mac=self.profile.mac,
                       user=self.student.user,
                       date=timezone.now().date() - timezone.timedelta(days=9))
        CheckInFactory(mac=self.profile.mac,
                       user=self.student.user,
                       date=timezone.now().date() - timezone.timedelta(days=7))

        self.profile.mac = faker.mac_address()
        self.profile.save()

        CheckInFactory(mac=self.profile.mac,
                       user=self.student.user,
                       date=timezone.now().date() - timezone.timedelta(days=5))
        CheckInFactory(mac=self.profile.mac,
                       user=self.student.user,
                       date=timezone.now().date() - timezone.timedelta(days=3))

        calculate_presence()

        self.course_assignment.refresh_from_db()
        self.assertEqual(self.course_assignment.student_presence, 100)
