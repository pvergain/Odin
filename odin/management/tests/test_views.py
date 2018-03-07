from test_plus import TestCase
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.utils import timezone

from odin.users.factories import BaseUserFactory, SuperUserFactory

from odin.interviews.models import Interviewer
from odin.education.factories import TeacherFactory, StudentFactory, CourseFactory
from odin.education.models import Student, Teacher, BaseUser, Course
from odin.applications.factories import ApplicationInfoFactory, ApplicationFactory, CompetitionFactory
from odin.competitions.factories import CompetitionTaskFactory

from odin.common.faker import faker


class TestManagementView(TestCase):
    def setUp(self):
        self.url = self.reverse('dashboard:management:index')
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)

    def test_user_passes_test_when_not_superuser(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.save()

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_user_passes_test_when_superuser(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_make_student_or_teacher_appears_if_user_is_not_student_or_teacher(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_superuser = True
        user.is_active = True
        user.save()

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertContains(response, 'Make Student')
            self.assertContains(response, 'Make Teacher')

    def test_make_student_does_not_appear_if_user_is_already_student(self):
        Student.objects.create_from_user(self.user)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertNotContains(response, 'Make Student')

    def test_make_teacher_does_not_appear_if_user_is_already_teacher(self):

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertNotContains(response, 'Make Teacher')
            self.assertContains(response, 'Make Student')

    def test_filter_students_shows_students(self):
        BaseUserFactory()
        Student.objects.create_from_user(self.user)

        with self.login(email=self.user.email, password=self.test_password):
            data = {
                'type': 'students'
            }

            response = self.get(self.url, data=data)
            self.assertEqual(1, len(response.context.get('object_list')))

    def test_filter_students_does_not_show_teachers(self):
        BaseUserFactory()
        TeacherFactory()
        Student.objects.create_from_user(self.user)

        with self.login(email=self.user.email, password=self.test_password):
            data = {
                'type': 'students'
            }

            response = self.get(self.url, data=data)
            self.assertEqual(1, len(response.context.get('object_list')))

    def test_filter_teachers_shows_teachers(self):
        BaseUserFactory()

        with self.login(email=self.user.email, password=self.test_password):
            data = {
                'type': 'teachers'
            }

            response = self.get(self.url, data=data)
            self.assertEqual(1, len(response.context.get('object_list')))

    def test_filter_teachers_does_not_show_students(self):
        BaseUserFactory()
        StudentFactory()

        with self.login(email=self.user.email, password=self.test_password):
            data = {
                'type': 'teachers'
            }

            response = self.get(self.url, data=data)
            self.assertEqual(1, len(response.context.get('object_list')))

    def test_filter_all_shows_all_users(self):
        StudentFactory()
        TeacherFactory()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(3, len(response.context.get('object_list')))

    def test_courses_are_shown_if_there_are_any(self):
        course = CourseFactory()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(1, len(response.context.get('courses')))
            self.assertContains(response, course.name)

    def test_courses_are_not_shown_if_there_are_none(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(0, len(response.context.get('courses')))


class TestCreateUserView(TestCase):
    def setUp(self):
        self.url = self.reverse('dashboard:management:add-user')
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)

    def test_get_is_forbidden_when_user_is_not_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_post_is_forbidden_when_user_is_not_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        with self.login(email=self.user.email, password=self.test_password):
            data = {'email': faker.email()}
            response = self.post(self.url, data=data)
            self.assertEqual(403, response.status_code)

    def test_post_creates_baseuser_when_user_is_superuser(self):
        with self.login(email=self.user.email, password=self.test_password):

            self.assertEqual(1, BaseUser.objects.count())

            data = {'email': faker.email()}
            response = self.post(self.url, data=data)
            self.assertRedirects(response=response, expected_url=self.reverse('dashboard:management:index'))
            self.assertEqual(2, BaseUser.objects.count())


class TestCreateStudentView(TestCase):
    def setUp(self):
        self.url = self.reverse('dashboard:management:add-student')
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)

    def test_get_is_forbidden_when_user_is_not_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_post_is_forbidden_when_user_is_not_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        with self.login(email=self.user.email, password=self.test_password):
            data = {'email': faker.email()}
            response = self.post(self.url, data=data)
            self.assertEqual(403, response.status_code)

    def test_post_creates_student_when_user_is_superuser(self):
        with self.login(email=self.user.email, password=self.test_password):
            self.assertEqual(0, Student.objects.count())

            data = {'email': faker.email()}
            response = self.post(self.url, data=data)
            self.assertRedirects(response=response, expected_url=self.reverse('dashboard:management:index'))
            self.assertEqual(1, Student.objects.count())


class TestCreateTeacherView(TestCase):
    def setUp(self):
        self.url = self.reverse('dashboard:management:add-teacher')
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)

    def test_get_is_forbidden_when_user_is_not_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_post_is_forbidden_when_user_is_not_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        with self.login(email=self.user.email, password=self.test_password):
            data = {'email': faker.email()}
            response = self.post(self.url, data=data)
            self.assertEqual(403, response.status_code)

    def test_post_creates_teacher_when_user_is_superuser(self):

        with self.login(email=self.user.email, password=self.test_password):
            self.assertEqual(1, Teacher.objects.count())

            data = {'email': faker.email()}
            response = self.post(self.url, data=data)
            self.assertRedirects(response=response, expected_url=self.reverse('dashboard:management:index'))
            self.assertEqual(2, Teacher.objects.count())


class TestPromoteUserToStudentView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)
        self.url = reverse('dashboard:management:promote-to-student', kwargs={'id': self.user.id})

    def test_get_is_forbidden_when_user_is_not_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_can_make_student_successfully(self):
        with self.login(email=self.user.email, password=self.test_password):
            self.assertEqual(0, Student.objects.count())
            self.assertEqual(1, BaseUser.objects.count())

            response = self.get(self.url)
            self.assertRedirects(response=response, expected_url=reverse('dashboard:management:index'))
            self.assertEqual(1, Student.objects.count())
            self.assertEqual(1, BaseUser.objects.count())


class TestPromoteUserToTeacherView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)
        self.url = reverse('dashboard:management:promote-to-teacher', kwargs={'id': self.user.id})

    def test_get_is_forbidden_when_user_is_not_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_can_make_teacher_successfully(self):
        user = BaseUserFactory()
        user.is_active = True
        user.save()

        with self.login(email=self.user.email, password=self.test_password):
            self.assertEqual(1, Teacher.objects.count())
            self.assertEqual(2, BaseUser.objects.count())

            response = self.get(reverse('dashboard:management:promote-to-teacher', kwargs={'id': user.id}))
            self.assertRedirects(response=response, expected_url=reverse('dashboard:management:index'))
            self.assertEqual(2, Teacher.objects.count())
            self.assertEqual(2, BaseUser.objects.count())


class TestCreateCourseView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)
        self.url = reverse('dashboard:management:add-course')

    def test_get_is_allowed_when_user_is_superuser(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_get_is_forbidden_for_regular_user(self):
        user = BaseUserFactory(password=self.test_password)
        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_course_is_created_successfully_on_post(self):
        self.assertEqual(0, Course.objects.count())
        start_date = faker.date_object()
        data = {
            'name': faker.word(),
            'start_date': start_date,
            'end_date': start_date + timezone.timedelta(days=faker.pyint()),
            'repository': faker.url(),
            'video_channel': faker.url(),
            'facebook_group': faker.url(),
            'slug_url': faker.slug(),
        }
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertRedirects(response, expected_url=reverse('dashboard:education:user-course-detail',
                                                                kwargs={'course_id': Course.objects.last().id}))
            self.assertEqual(1, Course.objects.count())


class TestAddTeacherToCourseView(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)
        self.url = reverse('dashboard:management:add-teacher-to-course')

    def test_adding_superuser_as_actual_teacher_makes_him_visible_for_course(self):
        self.assertNotIn(self.user.teacher, self.course.visible_teachers)

        data = {
            'teacher': self.user.id,
            'course': self.course.id
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertRedirects(response, expected_url=reverse('dashboard:management:index'))
            self.assertIn(self.user.teacher, self.course.visible_teachers)


class TestAddCourseToInterViewerCoursesView(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.test_password = faker.password()
        self.interviewer = Interviewer.objects.create_from_user(SuperUserFactory(password=self.test_password))
        self.interviewer.is_superuser = True
        self.interviewer.save()
        self.url = reverse('dashboard:management:add-interviewer-to-course')

    def test_post_does_not_add_course_when_course_does_not_have_application_info(self):
        current_course_count = self.interviewer.courses_to_interview.count()

        data = {
            'interviewer': self.interviewer.id,
            'course': self.course.id

        }

        with self.login(email=self.interviewer.email, password=self.test_password):
            self.post(self.url, data=data)
            self.interviewer.refresh_from_db()
            self.assertEqual(current_course_count, self.interviewer.courses_to_interview.count())

    def test_post_adds_course_when_course_has_have_application_info(self):
        ApplicationInfoFactory(course=self.course)
        self.course.refresh_from_db()

        data = {
            'interviewer': self.interviewer.id,
            'course': self.course.id

        }

        with self.login(email=self.interviewer.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.assertRedirects(response, expected_url=reverse('dashboard:management:index'))
            self.assertIn(self.course.application_info, self.interviewer.courses_to_interview.all())


class TestApplicationAddInterviewPersonView(TestCase):
    def setUp(self):
        self.application = ApplicationFactory()
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)
        self.management_id = self.application.application_info.id
        self.url = reverse('dashboard:management:application-interview-person',
                           kwargs={'application_id': self.application.id})

    def test_successfully_submited_data(self):
        with self.login(email=self.user.email, password=self.test_password):
            data = {
                'interview_person': self.user.id,
                'management_id': self.management_id
            }
            response = self.post(self.url, data=data, follow=False)
            self.assertEqual(200, response.status_code)

    def test_cannot_add_interviewer_to_application(self):
        self.application.application_info.end_date = datetime(2018, 2, 28)
        self.application.save()
        with self.login(email=self.user.email, password=self.test_password):
            data = {
                'interview_person': self.user.id,
                'management_id': self.management_id
            }
            self.response = self.client.post(self.url, data=data, follow=True)
            self.assertContains(self.response,
                                f'The interview period for {self.application.application_info.course} has expired!')


class TestAccessApplicationsManagementHidden(TestCase):
    def setUp(self):
        self.competition = CompetitionFactory()
        self.tasks = [CompetitionTaskFactory(competition=self.competition) for i in range(3)]
        self.start_date = timezone.now().date()
        self.end_date = timezone.now().date() + timedelta(days=10)
        self.start_interview_date = self.end_date + timedelta(days=1)
        self.end_interview_date = self.end_date + timedelta(days=5)
        self.application_info = ApplicationInfoFactory(start_date=self.start_date,
                                                       end_date=self.end_date, start_interview_date=self.start_interview_date,
                                                       end_interview_date=self.end_interview_date)
        self.competition.application_info = self.application_info
        self.competition.save()
        self.application = ApplicationFactory(application_info=self.application_info)
        self.application.save()
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)
        self.management_id = self.application.application_info.id
        self.url = reverse('dashboard:management:applications', kwargs={'application_info_id': self.management_id})

    def test_successful_access_with_superuser(self):
        import ipdb; ipdb.set_trace()
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url, follow=True)
            self.assertEqual(200, response.status_code)
