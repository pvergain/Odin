from test_plus import TestCase

from django.utils import timezone

from odin.common.faker import faker
from odin.education.models import Course
from odin.users.factories import SuperUserFactory


class TestPopulateCourseTeachersSignal(TestCase):
    def setUp(self):
        for i in range(5):
            SuperUserFactory()

    def test_create_course_populates_teachers_with_superusers(self):
        start_date = faker.date_object()
        course = Course.objects.create(name=faker.word(),
                                       start_date=start_date,
                                       end_date=start_date + timezone.timedelta(days=faker.pyint()),
                                       slug_url=faker.slug())
        self.assertEqual(5, course.teachers.count())
