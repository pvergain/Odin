from test_plus import TestCase

from django.urls import reverse

from ..services import add_student, add_teacher
from ..factories import (
    CourseFactory,
    StudentFactory,
    TeacherFactory,
    WeekFactory,
    TopicFactory,
    MaterialFactory,
    IncludedMaterialFactory,
)
from ..models import Student, Teacher, Topic, IncludedMaterial, Material

from odin.users.factories import ProfileFactory, BaseUserFactory

from odin.common.faker import faker


class TestUserCoursesView(TestCase):

    def setUp(self):
        self.test_password = faker.password()
        self.course = CourseFactory()
        self.student = StudentFactory(password=self.test_password)
        self.teacher = TeacherFactory(password=self.test_password)
        self.url = reverse('dashboard:education:user-courses')
        self.student.is_active = True
        self.teacher.is_active = True
        self.student.save()
        self.teacher.save()

    def test_get_course_list_view_when_logged_in(self):
        with self.login(email=self.student.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_get_course_list_redirects_to_login_when_not_logged(self):
        response = self.get(self.url)
        self.assertEqual(302, response.status_code)

    def test_course_is_not_shown_if_student_is_not_in_it(self):
        course = CourseFactory(name="TestCourseName")
        with self.login(email=self.student.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertNotIn(course.name, response.content.decode('utf-8'))

    def test_user_courses_are_shown_for_student_in_course(self):
        with self.login(email=self.student.email, password=self.test_password):
            add_student(self.course, self.student)
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertContains(response, self.course.name)

    def test_course_is_not_shown_if_teacher_is_not_in_it(self):
        course = CourseFactory(name="TestCourseName")
        with self.login(email=self.teacher.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertNotContains(response, course.name)

    def test_user_courses_are_shown_for_teacher_in_course(self):
        course = CourseFactory(name="TestCourseName")
        with self.login(email=self.teacher.email, password=self.test_password):
            add_teacher(course, self.teacher)
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertContains(response, course.name)

    def test_course_is_shown_if_user_is_teacher_and_student_in_different_courses(self):
        course = CourseFactory(name="TestCourseName")
        student = Student.objects.create_from_user(self.teacher.user)
        student.is_active = True
        student.save()
        with self.login(email=self.teacher.email, password=self.test_password):
            add_teacher(self.course, self.teacher)
            add_student(course, student)
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertContains(response, self.course.name)
            self.assertContains(response, course.name)


class TestCourseDetailView(TestCase):

    def setUp(self):
        self.test_password = faker.password()
        self.course = CourseFactory()
        self.student = StudentFactory(password=self.test_password)
        self.teacher = TeacherFactory(password=self.test_password)
        self.url = reverse('dashboard:education:user-course-detail', kwargs={'course_id': self.course.pk})
        self.student.is_active = True
        self.teacher.is_active = True
        self.student.save()
        self.teacher.save()

    def test_can_not_access_course_detail_if_not_student_or_teacher(self):
        response = self.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_can_access_course_detail_if_student(self):
        add_student(self.course, self.student)
        with self.login(email=self.student.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_course_teachers_appear_if_there_is_any(self):
        ProfileFactory(user=self.teacher.user)
        add_teacher(self.course, self.teacher)
        add_student(self.course, self.student)
        with self.login(email=self.student.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertContains(response, self.teacher.get_full_name())
            self.assertContains(response, self.teacher.profile.description)

    def test_course_teachers_do_not_appear_if_there_is_none(self):
        ProfileFactory(user=self.teacher.user)
        add_student(self.course, self.student)
        with self.login(email=self.student.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertNotContains(response, self.teacher.get_full_name())
            self.assertNotContains(response, self.teacher.profile.description)


class TestPublicCourseDetailView(TestCase):

    def setUp(self):
        self.course = CourseFactory()
        self.url = reverse('public:course_detail', kwargs={'course_slug': self.course.slug_url})

    def test_cannot_add_topic_or_material_on_public_detail_page(self):
        response = self.get(self.url)
        self.assertEqual(200, response.status_code)
        content = response.content.decode('utf-8')
        self.assertNotIn(content,
                         "<button type='button' name='button' class='btn green uppercase' >Add new topic</button>")
        self.assertNotIn(content,
                         "<button type='button' name='button' class='btn green uppercase' >Add new material</button>")


class TestAddTopicToCourseView(TestCase):

    def setUp(self):
        self.course = CourseFactory()
        self.week = WeekFactory(course=self.course)
        self.url = reverse('dashboard:education:course-management:manage-course-topics',
                           kwargs={'course_id': self.course.id})
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)

    def test_get_is_forbidden_if_not_teacher_for_course(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_get_is_allowed_when_teacher_for_course(self):
        teacher = Teacher.objects.create_from_user(self.user)
        add_teacher(self.course, teacher)
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_can_create_topic_for_course_on_post(self):
        data = {
            'name': faker.name(),
            'week': self.week.id
        }
        teacher = Teacher.objects.create_from_user(self.user)
        add_teacher(self.course, teacher)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertRedirects(response,
                                 expected_url=reverse('dashboard:education:user-course-detail',
                                                      kwargs={'course_id': self.course.id}))
            self.assertEqual(1, Topic.objects.count())
            self.assertEqual(1, Topic.objects.filter(course=self.course).count())


class TestAddNewIncludedMaterialView(TestCase):

    def setUp(self):
        self.course = CourseFactory()
        self.week = WeekFactory(course=self.course)
        self.topic = TopicFactory(course=self.course, week=self.week)
        self.url = reverse('dashboard:education:course-management:add-new-included-material',
                           kwargs={'course_id': self.course.id,
                                   'topic_id': self.topic.id})
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)

    def test_get_is_forbidden_if_not_teacher_for_course(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_get_is_allowed_when_teacher_for_course(self):
        teacher = Teacher.objects.create_from_user(self.user)
        add_teacher(self.course, teacher)
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_can_create_new_material_for_topic_on_post(self):
        teacher = Teacher.objects.create_from_user(self.user)
        add_teacher(self.course, teacher)
        data = {
            'identifier': faker.name(),
            'url': faker.url(),
            'content': faker.text(),
            'topic': self.topic.id,
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertRedirects(response, expected_url=reverse(
                'dashboard:education:user-course-detail',
                kwargs={'course_id': self.course.id}
            ))
            self.assertEqual(1, IncludedMaterial.objects.count())
            self.assertEqual(1, self.topic.materials.count())


class TestAddIncludedMaterialFromExistingView(TestCase):

    def setUp(self):
        self.course = CourseFactory()
        self.week = WeekFactory(course=self.course)
        self.topic = TopicFactory(course=self.course, week=self.week)
        self.url = reverse('dashboard:education:course-management:add-included-material-from-existing',
                           kwargs={'course_id': self.course.id,
                                   'topic_id': self.topic.id})
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)

    def test_get_is_forbidden_if_not_teacher_for_course(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_get_is_allowed_when_teacher_for_course(self):
        teacher = Teacher.objects.create_from_user(self.user)
        add_teacher(self.course, teacher)
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_existing_ordinary_material_is_shown_on_page(self):
        teacher = Teacher.objects.create_from_user(self.user)
        add_teacher(self.course, teacher)
        material = MaterialFactory()
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertContains(response, material.identifier)

    def test_can_add_ordinary_material_to_course(self):
        self.assertEqual(0, IncludedMaterial.objects.count())
        teacher = Teacher.objects.create_from_user(self.user)
        material = MaterialFactory()
        add_teacher(self.course, teacher)
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            response = self.post(self.url, data={'material_identifier': material.identifier})
            self.assertEqual(1, IncludedMaterial.objects.count())
            included_material = IncludedMaterial.objects.filter(material=material)
            self.assertEqual(1, Topic.objects.filter(materials__in=included_material).count())

    def test_can_add_included_material_from_existing_included_materials(self):
        course = CourseFactory()
        topic = TopicFactory(course=course)
        teacher = Teacher.objects.create_from_user(self.user)
        add_teacher(self.course, teacher)
        included_material = IncludedMaterialFactory(topic=topic)
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            response = self.post(self.url, data={'material_identifier': included_material.material.identifier})
            self.assertRedirects(response, expected_url=reverse(
                'dashboard:education:user-course-detail',
                kwargs={'course_id': self.course.id}))
            self.assertEqual(2, IncludedMaterial.objects.count())
            self.assertEqual(1, Material.objects.count())
