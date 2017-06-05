from datetime import timedelta

from test_plus import TestCase

from django.core.exceptions import ValidationError

from odin.common.faker import faker
from odin.common.utils import get_now

from odin.users.models import BaseUser
from odin.users.factories import BaseUserFactory

from ..factories import (StudentFactory, TeacherFactory, CourseFactory,
                         CourseWithStudentCourseAssignmentFactory,
                         CourseWithTeacherCourseAssignmentFactory,
                         CourseAssignmentStudentFactory,
                         CourseAssignmentTeacherFactory)
from ..models import Student, Teacher, CourseAssignment, Course


class StudentTests(TestCase):
    def test_creating_single_student_works(self):
        self.assertEqual(0, Student.objects.count())

        email, password = faker.email(), faker.password()
        Student.objects.create(email=email, password=password)

        self.assertEqual(1, Student.objects.count())

        student = Student.objects.first()

        self.assertEqual(email, student.email)
        self.assertTrue(student.user.check_password(password))

        self.assertIsNotNone(student.user.downcast(Student))

    def test_creating_from_baseuser_that_is_not_teacher_and_student_works(self):
        user = BaseUserFactory()

        self.assertEqual(0, Student.objects.count())

        student = Student.objects.create_from_user(user)

        self.assertEqual(1, Student.objects.count())

        self.assertEqual(user.email, student.email)
        self.assertTrue(student.user.check_password(BaseUserFactory.password))

        self.assertIsNotNone(student.user.downcast(Student))

    def test_creating_from_baseuser_for_existing_student_raises_validation_error(self):
        student = StudentFactory()

        with self.assertRaises(ValidationError):
            Student.objects.create_from_user(student.user)

    def test_creating_from_baseuser_that_is_teacher_works(self):
        teacher = TeacherFactory()

        self.assertEqual(0, Student.objects.count())

        student = Student.objects.create_from_user(teacher.user)

        self.assertEqual(1, Student.objects.count())
        self.assertEqual(1, Teacher.objects.count())
        self.assertEqual(1, BaseUser.objects.count())

        self.assertEqual(teacher.user.email, student.email)
        self.assertTrue(student.user.check_password(TeacherFactory.password))

        user = BaseUser.objects.first()

        self.assertIsNotNone(user.downcast(Student))
        self.assertIsNotNone(user.downcast(Teacher))


class TeacherTests(TestCase):
    def test_creating_single_teacher_works(self):
        self.assertEqual(0, Teacher.objects.count())

        email, password = faker.email(), faker.password()
        Teacher.objects.create(email=email, password=password)

        self.assertEqual(1, Teacher.objects.count())

        teacher = Teacher.objects.first()

        self.assertEqual(email, teacher.email)
        self.assertTrue(teacher.user.check_password(password))

        self.assertIsNotNone(teacher.user.downcast(Teacher))

    def test_creating_from_baseuser_that_is_not_teacher_and_student_works(self):
        user = BaseUserFactory()

        self.assertEqual(0, Teacher.objects.count())

        teacher = Teacher.objects.create_from_user(user)

        self.assertEqual(1, Teacher.objects.count())

        self.assertEqual(user.email, teacher.email)
        self.assertTrue(teacher.user.check_password(BaseUserFactory.password))

        self.assertIsNotNone(teacher.user.downcast(Teacher))

    def test_creating_from_baseuser_for_existing_teacher_raises_validation_error(self):
        teacher = TeacherFactory()

        with self.assertRaises(ValidationError):
            Teacher.objects.create_from_user(teacher.user)

    def test_creating_from_baseuser_that_is_student_works(self):
        student = StudentFactory()

        self.assertEqual(0, Teacher.objects.count())

        teacher = Teacher.objects.create_from_user(student.user)

        self.assertEqual(1, Student.objects.count())
        self.assertEqual(1, Teacher.objects.count())
        self.assertEqual(1, BaseUser.objects.count())

        self.assertEqual(student.user.email, teacher.email)
        self.assertTrue(teacher.user.check_password(StudentFactory.password))

        user = BaseUser.objects.first()

        self.assertIsNotNone(user.downcast(Student))
        self.assertIsNotNone(user.downcast(Teacher))


class BaseUserToStudentAndTeacherTests(TestCase):
    def test_create_teacher_and_student_from_baseuser_works(self):
        user = BaseUserFactory()

        self.assertIsNone(user.downcast(Student))
        self.assertIsNone(user.downcast(Teacher))
        self.assertEqual(0, Student.objects.count())
        self.assertEqual(0, Teacher.objects.count())
        self.assertEqual(1, BaseUser.objects.count())

        """
        First, create a student
        """
        Student.objects.create_from_user(user)

        self.assertIsNotNone(user.downcast(Student))
        self.assertIsNone(user.downcast(Teacher))

        self.assertEqual(1, Student.objects.count())
        self.assertEqual(0, Teacher.objects.count())
        self.assertEqual(1, BaseUser.objects.count())

        """
        Second, create a teacher
        """
        Teacher.objects.create_from_user(user)

        self.assertIsNotNone(user.downcast(Student))
        self.assertIsNotNone(user.downcast(Teacher))

        self.assertEqual(1, Student.objects.count())
        self.assertEqual(1, Teacher.objects.count())
        self.assertEqual(1, BaseUser.objects.count())


class CourseAssignmentTests(TestCase):
    def test_creating_course_assignment_with_only_course_raises_validation_error(self):
        course = CourseFactory()

        with self.assertRaises(ValidationError):
            CourseAssignment.objects.create(course=course)


class CourseTests(TestCase):
    def test_teachers_property_works(self):
        course = CourseFactory()
        teacher = TeacherFactory()

        self.assertEqual(0, course.teachers.count())

        CourseAssignment.objects.create(course=course,
                                        teacher=teacher)

        self.assertEqual(1, course.teachers.count())
        self.assertEqual(teacher, course.teachers.first().downcast(Teacher))

    def test_students_property_works(self):
        course = CourseFactory()
        student = StudentFactory()

        self.assertEqual(0, course.students.count())

        CourseAssignment.objects.create(course=course,
                                        student=student)

        self.assertEqual(1, course.students.count())
        self.assertEqual(student, course.students.first().downcast(Student))

    def test_students_and_teachers_properties_work_for_user_that_is_both(self):
        course = CourseFactory()

        student = StudentFactory()
        teacher = Teacher.objects.create_from_user(student.user)

        self.assertEqual(0, course.students.count())
        self.assertEqual(0, course.teachers.count())

        CourseAssignment.objects.create(course=course,
                                        student=student)

        CourseAssignment.objects.create(course=course,
                                        teacher=teacher)

        self.assertEqual(1, course.students.count())
        self.assertEqual(1, course.teachers.count())

        self.assertEqual(student, course.students.first().downcast(Student))
        self.assertEqual(teacher, course.teachers.first().downcast(Teacher))

    def test_course_has_started_if_start_date_is_in_the_past(self):
        start_date = (get_now() - timedelta(days=1)).date()
        end_date = (get_now() + timedelta(days=1)).date()

        course = CourseFactory(start_date=start_date,
                               end_date=end_date)

        self.assertTrue(course.has_started)

    def test_course_has_started_if_start_date_is_today(self):
        start_date = get_now().date()
        end_date = (get_now() + timedelta(days=1)).date()

        course = CourseFactory(start_date=start_date,
                               end_date=end_date)

        self.assertTrue(course.has_started)

    def test_course_has_not_started_if_start_date_is_in_the_future(self):
        start_date = (get_now() + timedelta(days=1)).date()
        end_date = (get_now() + timedelta(days=2)).date()

        course = CourseFactory(start_date=start_date,
                               end_date=end_date)

        self.assertFalse(course.has_started)

    def test_creating_course_with_student_or_teacher(self):
        for i in range(3):
            StudentFactory()

        teacher = TeacherFactory()
        CourseAssignmentTeacherFactory(teacher=teacher)
        CourseAssignmentStudentFactory(student=Student.objects.first())
        self.assertEqual(2, Course.objects.count())

    def test_create_course_with_multiple_students(self):
        for i in range(3):
            StudentFactory()

        course = CourseWithTeacherCourseAssignmentFactory()
        CourseAssignmentStudentFactory(course=course)
        CourseAssignmentStudentFactory(course=course)
        course = Course.objects.first()
        self.assertEqual(2, course.students.count())

    def test_course_has_finished(self):
        start_date = (get_now() + timedelta(days=1)).date()
        end_date = (get_now() + timedelta(days=2)).date()
        course = CourseFactory(start_date=start_date, end_date=end_date)
        start_date = (get_now() - timedelta(days=1)).date()
        end_date = get_now().date()
        course2 = CourseFactory(start_date=start_date, end_date=end_date)
        self.assertFalse(course.has_finished)
        self.assertTrue(course2.has_finished)

    def test_can_generate_certificates(self):
        start_date = (get_now() + timedelta(days=1)).date()
        end_date = (get_now() + timedelta(days=2)).date()
        course = CourseFactory(start_date=start_date, end_date=end_date)
        start_date = (get_now() - timedelta(days=30)).date()
        end_date = (get_now() - timedelta(days=16)).date()
        course2 = CourseFactory(start_date=start_date, end_date=end_date)
        self.assertTrue(course.can_generate_certificates)
        self.assertFalse(course2.can_generate_certificates)

    def test_duration_in_weeks(self):
        start_date = get_now().date()
        end_date = (get_now() + timedelta(days=13)).date()
        course = CourseFactory(start_date=start_date, end_date=end_date)
        end_date = (get_now() + timedelta(days=14)).date()
        course2 = CourseFactory(start_date=start_date, end_date=end_date)
        self.assertEqual(2, course.duration_in_weeks)
        self.assertEqual(3, course2.duration_in_weeks)
