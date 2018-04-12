from datetime import timedelta

from test_plus import TestCase

from django.core.exceptions import ValidationError

from odin.common.faker import faker
from odin.common.utils import get_now

from odin.users.models import BaseUser
from odin.users.factories import BaseUserFactory

from ..factories import (
    StudentFactory,
    TeacherFactory,
    CourseFactory,
    IncludedTaskFactory,
    SolutionFactory,
    WeekFactory
)
from ..models import Student, Teacher, CourseAssignment, IncludedTask, Solution
from ..services import add_student, add_teacher


class StudentTests(TestCase):
    def test_creating_single_student_works(self):
        count = Student.objects.count()

        email, password = faker.email(), faker.password()
        Student.objects.create(email=email, password=password)

        self.assertEqual(count + 1, Student.objects.count())

        student = Student.objects.first()

        self.assertEqual(email, student.email)
        self.assertTrue(student.user.check_password(password))

        self.assertIsNotNone(student.user.downcast(Student))

    def test_creating_from_baseuser_that_is_not_teacher_and_student_works(self):
        user = BaseUserFactory()

        count = Student.objects.count()

        student = Student.objects.create_from_user(user)

        self.assertEqual(count + 1, Student.objects.count())

        self.assertEqual(user.email, student.email)
        self.assertTrue(student.user.check_password(BaseUserFactory.password))

        self.assertIsNotNone(student.user.downcast(Student))

    def test_creating_from_baseuser_for_existing_student_raises_validation_error(self):
        student = StudentFactory()

        with self.assertRaises(ValidationError):
            Student.objects.create_from_user(student.user)

    def test_creating_from_baseuser_that_is_teacher_works(self):
        teacher = TeacherFactory()

        teacher_count = Teacher.objects.count()
        user_count = BaseUser.objects.count()
        student_count = Student.objects.count()

        student = Student.objects.create_from_user(teacher.user)

        self.assertEqual(student_count + 1, Student.objects.count())
        self.assertEqual(teacher_count, Teacher.objects.count())
        self.assertEqual(user_count, BaseUser.objects.count())

        self.assertEqual(teacher.user.email, student.email)
        self.assertTrue(student.user.check_password(TeacherFactory.password))

        user = BaseUser.objects.first()

        self.assertIsNotNone(user.downcast(Student))
        self.assertIsNotNone(user.downcast(Teacher))


class TeacherTests(TestCase):
    def test_creating_single_teacher_works(self):
        count = Teacher.objects.count()

        email, password = faker.email(), faker.password()
        Teacher.objects.create(email=email, password=password)

        self.assertEqual(count + 1, Teacher.objects.count())

        teacher = Teacher.objects.first()

        self.assertEqual(email, teacher.email)
        self.assertTrue(teacher.user.check_password(password))

        self.assertIsNotNone(teacher.user.downcast(Teacher))

    def test_creating_from_baseuser_that_is_not_teacher_and_student_works(self):
        user = BaseUserFactory()

        count = Teacher.objects.count()

        teacher = Teacher.objects.create_from_user(user)

        self.assertEqual(count + 1, Teacher.objects.count())

        self.assertEqual(user.email, teacher.email)
        self.assertTrue(teacher.user.check_password(BaseUserFactory.password))

        self.assertIsNotNone(teacher.user.downcast(Teacher))

    def test_creating_from_baseuser_for_existing_teacher_raises_validation_error(self):
        teacher = TeacherFactory()

        with self.assertRaises(ValidationError):
            Teacher.objects.create_from_user(teacher.user)

    def test_creating_from_baseuser_that_is_student_works(self):
        student = StudentFactory()

        teacher_count = Teacher.objects.count()
        student_count = Student.objects.count()
        user_count = BaseUser.objects.count()

        teacher = Teacher.objects.create_from_user(student.user)

        self.assertEqual(student_count, Student.objects.count())
        self.assertEqual(teacher_count + 1, Teacher.objects.count())
        self.assertEqual(user_count, BaseUser.objects.count())

        self.assertEqual(student.user.email, teacher.email)
        self.assertTrue(teacher.user.check_password(StudentFactory.password))

        user = BaseUser.objects.first()

        self.assertIsNotNone(user.downcast(Student))
        self.assertIsNotNone(user.downcast(Teacher))


class BaseUserToStudentAndTeacherTests(TestCase):
    def test_create_teacher_and_student_from_baseuser_works(self):
        user = BaseUserFactory()

        teacher_count = Teacher.objects.count()
        student_count = Student.objects.count()
        user_count = BaseUser.objects.count()

        self.assertIsNone(user.downcast(Student))
        self.assertIsNone(user.downcast(Teacher))

        """
        First, create a student
        """
        Student.objects.create_from_user(user)

        self.assertIsNotNone(user.downcast(Student))
        self.assertIsNone(user.downcast(Teacher))

        self.assertEqual(student_count + 1, Student.objects.count())
        self.assertEqual(teacher_count, Teacher.objects.count())
        self.assertEqual(user_count, BaseUser.objects.count())

        """
        Second, create a teacher
        """
        Teacher.objects.create_from_user(user)

        self.assertIsNotNone(user.downcast(Student))
        self.assertIsNotNone(user.downcast(Teacher))

        self.assertEqual(student_count + 1, Student.objects.count())
        self.assertEqual(teacher_count + 1, Teacher.objects.count())
        self.assertEqual(user_count, BaseUser.objects.count())


class CourseAssignmentTests(TestCase):
    def test_creating_course_assignment_with_only_course_raises_validation_error(self):
        course = CourseFactory()

        with self.assertRaises(ValidationError):
            CourseAssignment.objects.create(course=course)


class CourseTests(TestCase):
    def test_teachers_property_works(self):
        course = CourseFactory()
        teacher = TeacherFactory()

        count = course.visible_teachers.count()

        CourseAssignment.objects.create(course=course,
                                        teacher=teacher)

        self.assertEqual(count + 1, course.teachers.count())
        self.assertEqual(teacher, course.teachers.first().downcast(Teacher))

    def test_students_property_works(self):
        course = CourseFactory()
        student = StudentFactory()

        count = course.students.count()

        CourseAssignment.objects.create(course=course,
                                        student=student)

        self.assertEqual(count + 1, course.students.count())
        self.assertEqual(student, course.students.first().downcast(Student))

    def test_students_and_teachers_properties_work_for_user_that_is_both(self):
        course = CourseFactory()

        student = StudentFactory()
        teacher = Teacher.objects.create_from_user(student.user)

        student_count = course.students.count()
        teacher_count = course.teachers.count()

        CourseAssignment.objects.create(course=course,
                                        student=student)

        CourseAssignment.objects.create(course=course,
                                        teacher=teacher)

        self.assertEqual(student_count + 1, course.students.count())
        self.assertEqual(teacher_count + 1, course.teachers.count())

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

    def test_create_course_with_multiple_students(self):
        students = StudentFactory.create_batch(3)
        course = CourseFactory()

        count = course.students.count()

        for student in students:
            add_student(course, student)

        self.assertEqual(count + 3, course.students.count())

    def test_create_course_with_multiple_teachers(self):
        teachers = TeacherFactory.create_batch(3)
        course = CourseFactory()

        count = course.teachers.count()

        for teacher in teachers:
            add_teacher(course, teacher)

        self.assertEqual(count + 3, course.teachers.count())

    def test_course_has_finished_with_end_date_today(self):
        start_date = (get_now() - timedelta(days=1)).date()
        end_date = get_now().date()
        course = CourseFactory(start_date=start_date, end_date=end_date)

        self.assertTrue(course.has_finished)

    def test_course_has_finished_with_end_date_bigger_than_today(self):
        start_date = (get_now() + timedelta(days=1)).date()
        end_date = (get_now() + timedelta(days=2)).date()
        course = CourseFactory(start_date=start_date, end_date=end_date)

        self.assertFalse(course.has_finished)

    def test_can_generate_certificates_with_end_date_in_time_gap(self):
        start_date = (get_now() + timedelta(days=1)).date()
        end_date = (get_now() + timedelta(days=2)).date()
        course = CourseFactory(start_date=start_date, end_date=end_date)

        self.assertTrue(course.can_generate_certificates)

    def test_can_generate_certificates_with_end_date_outside_time_gap(self):
        start_date = (get_now() - timedelta(days=30)).date()
        end_date = (get_now() - timedelta(days=16)).date()
        course = CourseFactory(start_date=start_date, end_date=end_date)

        self.assertFalse(course.can_generate_certificates)

    def test_duration_in_weeks_should_return_two(self):
        start_date = get_now().date()
        end_date = (get_now() + timedelta(days=13)).date()
        course = CourseFactory(start_date=start_date, end_date=end_date)

        self.assertEqual(2, course.duration_in_weeks)

    def test_duration_in_weeks_should_return_three(self):
        start_date = get_now().date()
        end_date = (get_now() + timedelta(days=14)).date()
        course2 = CourseFactory(start_date=start_date, end_date=end_date)

        self.assertEqual(3, course2.duration_in_weeks)


class TaskTests(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.week = WeekFactory(course=self.course)

    def test_get_tasks_for_course_returns_tasks_for_course(self):
        task = IncludedTaskFactory(course=self.course, week=self.week)
        queryset = IncludedTask.objects.get_tasks_for(self.course)
        self.assertEqual([task], list(queryset))

    def test_get_tasks_for_course_does_not_return_any_tasks_if_course_has_none(self):
        queryset = IncludedTask.objects.get_tasks_for(self.course)
        self.assertEqual([], list(queryset))


class SolutionTests(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.week = WeekFactory(course=self.course)
        self.user = BaseUserFactory()
        self.student = StudentFactory()
        add_student(self.course, self.student)
        self.task = IncludedTaskFactory(course=self.course, week=self.week, gradable=False)

    def test_get_solved_solutions_for_student_and_course_returns_solved_solutions(self):
        solution = SolutionFactory(task=self.task, user=self.user, status=Solution.SUBMITTED_WITHOUT_GRADING)

        queryset = Solution.objects.get_solved_solutions_for_student_and_course(self.user, self.course)
        self.assertEqual([solution], list(queryset))

    def test_get_solved_solutions_for_student_and_course_does_not_return_solutions_if_no_solutions(self):
        queryset = Solution.objects.get_solved_solutions_for_student_and_course(self.student, self.course)
        self.assertEqual([], list(queryset))

    def test_get_solved_solutions_for_student_and_course_returns_nothing_if_no_solved_solutions(self):
        self.task.gradable = True
        self.task.save()
        SolutionFactory(task=self.task, user=self.user, status=Solution.NOT_OK)

        queryset = Solution.objects.get_solved_solutions_for_student_and_course(self.student, self.course)
        self.assertEqual([], list(queryset))
