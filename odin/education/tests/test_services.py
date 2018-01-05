from test_plus import TestCase

from dateutil import parser
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.db.models import Q

from ..services import (
    create_course,
    create_topic,
    create_included_material,
    create_included_task,
    create_test_for_task,
    create_gradable_solution,
    create_non_gradable_solution,
    create_lecture
)
from ..models import (
    Course,
    Week,
    Topic,
    Material,
    IncludedMaterial,
    Task,
    IncludedTask,
    Solution,
    IncludedTest,
    Lecture
)
from ..factories import (
    CourseFactory,
    WeekFactory,
    TopicFactory,
    IncludedTaskFactory,
    ProgrammingLanguageFactory,
    StudentFactory,
)

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


class TestCreateIncludedTask(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.topic = TopicFactory(course=self.course)
        self.task = Task.objects.create(name="Test task",
                                        description=faker.text(),
                                        gradable=faker.boolean())

    def test_create_included_task_creates_only_included_task_when_existing_is_provided(self):
        current_task_count = Task.objects.count()
        current_included_task_count = IncludedTask.objects.count()

        create_included_task(existing_task=self.task, topic=self.topic)

        self.assertEqual(current_task_count, Task.objects.count())
        self.assertEqual(current_included_task_count + 1, IncludedTask.objects.count())

    def test_create_included_task_creates_task_and_included_task_when_no_existing_is_provided(self):
        current_task_count = Task.objects.count()
        current_included_task_count = IncludedTask.objects.count()
        create_included_task(name=faker.name(),
                             description=faker.text(),
                             gradable=faker.boolean(),
                             topic=self.topic)
        self.assertEqual(current_task_count + 1, Task.objects.count())
        self.assertEqual(current_included_task_count + 1, IncludedTask.objects.count())


class TestCreateTestForTask(TestCase):

    def setUp(self):
        self.topic = TopicFactory()
        self.included_task = IncludedTaskFactory(topic=self.topic, gradable=True)
        self.language = ProgrammingLanguageFactory()

    def test_create_test_for_task_raises_validation_error_when_no_resource_is_provided(self):
        with self.assertRaises(ValidationError):
            create_test_for_task(task=self.included_task,
                                 language=self.language)

    def test_create_test_for_task_raises_validation_error_when_both_resources_are_provided(self):
        with self.assertRaises(ValidationError):
            create_test_for_task(task=self.included_task,
                                 language=self.language,
                                 code=faker.text(),
                                 file=SimpleUploadedFile('text.bin', bytes(f'{faker.text()}'.encode('utf-8'))))

    def test_create_test_for_task_creates_source_code_test_when_code_is_provided(self):
        filters = {
            'code__isnull': False,
            'file': ''
        }

        current_source_code_test_count = IncludedTest.objects.filter(**filters).count()

        create_test_for_task(task=self.included_task,
                             language=self.language,
                             code=faker.text())

        self.assertEqual(current_source_code_test_count + 1, IncludedTest.objects.filter(**filters).count())

    def test_create_test_for_task_creates_binary_file_test_when_code_is_provided(self):
        filters = {
            'code__isnull': True,
        }

        current_binary_file_test_count = IncludedTest.objects.filter(~Q(file=''), **filters).count()

        create_test_for_task(task=self.included_task,
                             language=self.language,
                             file=SimpleUploadedFile('text.bin', bytes(f'{faker.text()}'.encode('utf-8'))))

        self.assertEqual(current_binary_file_test_count + 1, IncludedTest.objects.filter(**filters).count())

    def test_create_test_for_task_raises_validation_error_when_provided_task_is_not_gradable(self):
        with self.assertRaises(ValidationError):
            self.included_task.gradable = False
            self.included_task.save()

            create_test_for_task(task=self.included_task,
                                 language=self.language,
                                 code=faker.text())


class TestCreateGradableSolution(TestCase):
    def setUp(self):
        self.topic = TopicFactory()
        self.task = IncludedTaskFactory(topic=self.topic, gradable=True)
        self.student = StudentFactory()

    def test_create_gradable_solution_raises_validation_error_when_no_resource_is_provided(self):
        with self.assertRaises(ValidationError):
            create_gradable_solution(student=self.student,
                                     task=self.task)

    def test_create_gradable_solution_raises_validation_error_when_both_resources_are_provided(self):
        with self.assertRaises(ValidationError):
            create_gradable_solution(student=self.student,
                                     task=self.task,
                                     code=faker.text(),
                                     file=SimpleUploadedFile('text.bin', bytes(f'{faker.text()}'.encode('utf-8'))))

    def test_create_gradable_solution_creates_solution_with_code_when_code_is_provided(self):
        current_solution_count = Solution.objects.count()

        solution = create_gradable_solution(task=self.task,
                                            student=self.student,
                                            code=faker.text())

        self.assertEqual(current_solution_count + 1, Solution.objects.count())
        self.assertIsNotNone(solution.code)
        self.assertIsNone(solution.file.name)
        self.assertIsNone(solution.url)

    def test_create_gradable_solution_creates_solution_with_file_when_file_is_provided(self):
        current_solution_count = Solution.objects.count()

        solution = create_gradable_solution(task=self.task,
                                            student=self.student,
                                            file=SimpleUploadedFile('text.bin', bytes(f'{faker.text()}'
                                                                    .encode('utf-8'))))

        self.assertEqual(current_solution_count + 1, Solution.objects.count())
        self.assertIsNotNone(solution.file.name)
        self.assertIsNone(solution.code)
        self.assertIsNone(solution.url)


class TestCreateNonGradableSolution(TestCase):
    def setUp(self):
        self.topic = TopicFactory()
        self.task = IncludedTaskFactory(topic=self.topic, gradable=False)
        self.student = StudentFactory()

    def test_create_non_gradable_solution_raises_validation_error_when_no_resource_is_provided(self):
        with self.assertRaises(ValidationError):
            create_non_gradable_solution(student=self.student,
                                         task=self.task)

    def test_create_non_gradable_solution_creates_non_gradable_solution_with_url_when_url_is_provided(self):
        current_solution_count = Solution.objects.count()

        solution = create_non_gradable_solution(task=self.task,
                                                student=self.student,
                                                url=faker.url())

        self.assertEqual(current_solution_count + 1, Solution.objects.count())
        self.assertIsNotNone(solution.url)
        self.assertIsNone(solution.file.name)
        self.assertIsNone(solution.code)


class TestCreateLecture(TestCase):
    def setUp(self):
        start_date = timezone.now().date() + timezone.timedelta(days=faker.pyint())
        self.course = CourseFactory(start_date=start_date,
                                    end_date=start_date + timezone.timedelta(days=faker.pyint()))

    def test_service_creates_lecture_when_date_is_valid(self):
        valid_date = self.course.start_date + timezone.timedelta(days=1)
        current_lecture_count = Lecture.objects.count()
        create_lecture(date=valid_date, course=self.course)

        self.assertEqual(current_lecture_count + 1, Lecture.objects.count())

    def test_service_raises_validation_error_when_date_is_invalid(self):
        invalid_date = self.course.end_date + timezone.timedelta(days=faker.pyint())
        with self.assertRaises(ValidationError):
            create_lecture(date=invalid_date, course=self.course)
