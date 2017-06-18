from test_plus import TestCase

from django.core.urlresolvers import reverse

from odin.users.factories import BaseUserFactory, SuperUserFactory

from odin.education.factories import TeacherFactory, StudentFactory
from odin.education.models import Student, Teacher, BaseUser

from odin.common.faker import faker


class TestRedirectToDashboardIndexView(TestCase):
    def setUp(self):
        self.url = '/'
        self.test_password = faker.password()

    def test_get_redirects_to_login_when_no_user_logged(self):
        response = self.get(self.url, follow=True)
        expected = reverse('account_login') + '?next=/dashboard/'
        self.assertRedirects(response=response, expected_url=expected)

    def test_get_redirects_to_dashboard_index_when_user_logged(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.save()

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url, follow=True)
            self.assertRedirects(response=response, expected_url=self.reverse('dashboard:index'))


class TestManagementView(TestCase):
    def setUp(self):
        self.url = self.reverse('dashboard:management')
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
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertContains(response, "Make Student")
            self.assertContains(response, "Make Teacher")

    def test_make_student_does_not_appear_if_user_is_already_student(self):
        Student.objects.create_from_user(self.user)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertNotContains(response, "Make Student")
            self.assertContains(response, "Make Teacher")

    def test_make_teacher_does_not_appear_if_user_is_already_teacher(self):
        Teacher.objects.create_from_user(self.user)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertNotContains(response, "Make Teacher")
            self.assertContains(response, "Make Student")

    def test_can_make_student_successfully(self):
        url = reverse('dashboard:promote', kwargs={'type': 'student', 'id': self.user.id})

        with self.login(email=self.user.email, password=self.test_password):
            self.assertEqual(0, Student.objects.count())
            response = self.get(url)
            self.assertRedirects(response=response, expected_url=self.url)
            self.assertEqual(1, Student.objects.count())

    def test_can_make_teacher_successfully(self):
        url = reverse('dashboard:promote', kwargs={'type': 'teacher', 'id': self.user.id})

        with self.login(email=self.user.email, password=self.test_password):
            self.assertEqual(0, Teacher.objects.count())
            response = self.get(url)
            self.assertRedirects(response=response, expected_url=self.url)
            self.assertEqual(1, Teacher.objects.count())

    def test_filter_students_shows_students(self):
        Student.objects.create_from_user(self.user)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=students')
            self.assertEqual(1, len(response.context.get('object_list')))

    def test_filter_students_does_not_show_teachers(self):
        TeacherFactory()
        Student.objects.create_from_user(self.user)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=students')
            self.assertEqual(1, len(response.context.get('object_list')))

    def test_filter_teachers_shows_teachers(self):
        Teacher.objects.create_from_user(self.user)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=teachers')
            self.assertEqual(1, len(response.context.get('object_list')))

    def test_filter_teachers_does_not_show_students(self):
        StudentFactory()
        Teacher.objects.create_from_user(self.user)

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=teachers')
            self.assertEqual(1, len(response.context.get('object_list')))

    def test_filter_all_shows_all_users(self):
        StudentFactory()
        TeacherFactory()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=all')
            self.assertEqual(3, len(response.context.get('object_list')))

    def test_button_changes_on_no_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertResponseContains(response=response, text='<input class="btn green uppercase" value="Add user">')

    def test_button_changes_on_student_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=students')
            self.assertResponseContains(response=response,
                                        text='<input class="btn green uppercase" value="Add student">')

    def test_button_changes_on_all_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=all')
            self.assertResponseContains(response=response, text='<input class="btn green uppercase" value="Add user">')

    def test_button_changes_on_teacher_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=teachers')
            self.assertResponseContains(response=response,
                                        text='<input class="btn green uppercase" value="Add teacher">')


class TestManagementCreateUserView(TestCase):
    def setUp(self):
        self.url = self.reverse('dashboard:add-user')
        self.test_password = faker.password()
        self.user = SuperUserFactory(password=self.test_password)

    def test_title_changes_on_no_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertResponseContains(response=response, text='Add user')

    def test_title_changes_on_all_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=all')
            self.assertResponseContains(response=response, text='Add user')

    def test_title_changes_on_student_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=students')
            self.assertResponseContains(response=response, text='Add student')

    def test_title_changes_on_teacher_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url + '?filter=teachers')
            self.assertResponseContains(response=response, text='Add teacher')

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

    def test_post_creates_baseuser_on_no_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            data = {'email': faker.email()}
            response = self.post(self.url, data=data)
            self.assertRedirects(response=response, expected_url=self.reverse('dashboard:management'))
            self.assertEqual(2, BaseUser.objects.count())
            self.assertEqual(0, Student.objects.count())
            self.assertEqual(0, Teacher.objects.count())

    def test_post_creates_baseuser_on_students_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            data = {'email': faker.email()}
            response = self.post(self.url + '?filter=students', data=data)
            self.assertRedirects(response=response, expected_url=self.reverse('dashboard:management'))
            self.assertEqual(2, BaseUser.objects.count())
            self.assertEqual(1, Student.objects.count())
            self.assertEqual(0, Teacher.objects.count())

    def test_post_creates_baseuser_on_teachers_filter(self):
        with self.login(email=self.user.email, password=self.test_password):
            data = {'email': faker.email()}
            response = self.post(self.url + '?filter=teachers', data=data)
            self.assertRedirects(response=response, expected_url=self.reverse('dashboard:management'))
            self.assertEqual(2, BaseUser.objects.count())
            self.assertEqual(0, Student.objects.count())
            self.assertEqual(1, Teacher.objects.count())
