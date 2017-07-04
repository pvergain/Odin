from test_plus import TestCase

from odin.common.faker import faker
from odin.education.models import Course
from odin.users.factories import SuperUserFactory


class TestPopulateCourseTeachersSignal(TestCase):
    def setUp(self):
        for i in range(5):
            SuperUserFactory()

    def test_create_course_populates_teachers_with_superusers(self):
        course = Course.objects.create(name=faker.word(), start_date=faker.date(), end_date=faker.date())
        self.assertEqual(5, course.teachers.count())
