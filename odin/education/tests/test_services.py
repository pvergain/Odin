from test_plus import TestCase

from dateutil import parser
from datetime import timedelta

from django.core.exceptions import ValidationError

from ..services import create_course, create_topic, create_included_material
from ..models import Course, Week, Topic, Material, IncludedMaterial
from ..factories import CourseFactory, WeekFactory, TopicFactory

from odin.common.faker import faker


class TestCreateCourse(TestCase):

    def test_course_is_created_successfully_with_valid_data(self):
        start_date = parser.parse(faker.date())
        count = Course.objects.count()
        data = {
            'name': faker.word(),
            'start_date': start_date,
            'end_date': start_date + timedelta(days=faker.pyint()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
            'slug_url': faker.slug(),
        }
        create_course(**data)
        self.assertEqual(count + 1, Course.objects.count())

    def test_create_course_raises_error_on_duplicate_name(self):
        start_date = parser.parse(faker.date())
        course = CourseFactory()
        count = Course.objects.count()
        data = {
            'name': course.name,
            'start_date': start_date,
            'end_date': start_date + timedelta(days=faker.pyint()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
            'slug_url': faker.slug(),
        }
        with self.assertRaises(ValidationError):
            create_course(**data)
        self.assertEqual(count, Course.objects.count())

    def test_create_course_creates_weeks_for_course_successfully(self):
        start_date = parser.parse(faker.date())
        count = Course.objects.count()
        data = {
            'name': faker.word(),
            'start_date': start_date,
            'end_date': start_date + timedelta(days=faker.pyint()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
            'slug_url': faker.slug(),
        }
        course = create_course(**data)
        weeks = course.duration_in_weeks
        self.assertEqual(count + 1, Course.objects.count())
        self.assertEqual(weeks, Week.objects.count())

    def test_create_course_starts_week_from_monday(self):
        start_date = parser.parse(faker.date())
        data = {
            'name': faker.word(),
            'start_date': start_date,
            'end_date': start_date + timedelta(days=faker.pyint()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
            'slug_url': faker.slug(),
        }
        course = create_course(**data)
        weeks = course.duration_in_weeks
        self.assertEqual(1, Course.objects.count())
        self.assertEqual(weeks, Week.objects.count())
        week_one = Week.objects.first()
        self.assertEqual(0, week_one.start_date.weekday())


class TestCreateTopic(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.week = WeekFactory(course=self.course)

    def test_create_topic_adds_topic_to_course_successfully(self):
        topic_count = Topic.objects.count()
        course_topics_count = Topic.objects.filter(course=self.course).count()

        create_topic(name=faker.name(), course=self.course, week=self.week)

        self.assertEqual(topic_count + 1, Topic.objects.count())
        self.assertEqual(course_topics_count + 1, Topic.objects.filter(course=self.course).count())

    def test_create_topic_raises_validation_error_on_existing_topic(self):
        topic = create_topic(name=faker.name(), course=self.course, week=self.week)
        topic_count = Topic.objects.count()
        course_topics_count = Topic.objects.filter(course=self.course).count()

        with self.assertRaises(ValidationError):
            create_topic(name=topic.name, course=self.course, week=self.week)

        self.assertEqual(topic_count, Topic.objects.count())
        self.assertEqual(course_topics_count, Topic.objects.filter(course=self.course).count())


class TestCreateIncludedMaterial(TestCase):
    def setUp(self):
        self.topic = TopicFactory()
        self.material = Material.objects.create(identifier="TestMaterial",
                                                url=faker.url(),
                                                content=faker.text())

    def test_create_included_material_raises_validation_error_if_material_already_exists(self):
        with self.assertRaises(ValidationError):
            create_included_material(identifier=self.material.identifier,
                                     url=faker.url(),
                                     topic=self.topic)

    def test_create_included_material_creates_only_included_material_when_existing_is_provided(self):
        current_material_count = Material.objects.count()
        current_included_material_count = IncludedMaterial.objects.count()

        create_included_material(existing_material=self.material, topic=self.topic)

        self.assertEqual(current_material_count, Material.objects.count())
        self.assertEqual(current_included_material_count + 1, IncludedMaterial.objects.count())

    def test_create_included_material_creates_material_and_included_material_when_no_existing_is_provided(self):
        current_material_count = Material.objects.count()
        current_included_material_count = IncludedMaterial.objects.count()
        create_included_material(identifier=faker.word(),
                                 url=faker.url(),
                                 content=faker.text(),
                                 topic=self.topic)
        self.assertEqual(current_material_count + 1, Material.objects.count())
        self.assertEqual(current_included_material_count + 1, IncludedMaterial.objects.count())
