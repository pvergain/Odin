from test_plus import TestCase

from ..factories import IncludedTaskFactory, SolutionFactory, CourseFactory, StudentFactory
from ..models import Solution
from ..services import add_student
from ..utils import (
    get_passed_and_failed_tasks,
    get_solution_data,
    get_all_solved_student_solution_count_for_course,
)


class TestGetPassedAndFailedTasks(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.gradable_task = IncludedTaskFactory(topic__course=self.course, gradable=True)
        self.non_gradable_task = IncludedTaskFactory(topic__course=self.course, gradable=False)
        self.student = StudentFactory()
        add_student(course=self.course, student=self.student)

    def test_returns_task_passed_when_there_is_passing_solution_for_it(self):
        passing_gradable_solution = SolutionFactory(student=self.student, task=self.gradable_task, status=Solution.OK)
        passing_non_gradable_solution = SolutionFactory(
            student=self.student, task=self.non_gradable_task, status=Solution.SUBMITTED_WITHOUT_GRADING
        )

        solution_data = {
            self.gradable_task.name: [passing_gradable_solution],
            self.non_gradable_task.name: [passing_non_gradable_solution]
        }
        result = get_passed_and_failed_tasks(solution_data)
        self.assertEqual("Passed", result.get(self.gradable_task.name))
        self.assertEqual("Passed", result.get(self.non_gradable_task.name))

    def test_returns_task_failed_when_there_is_failing_solution_for_it(self):
        failing_solution = SolutionFactory(student=self.student, task=self.gradable_task, status=Solution.NOT_OK)
        solution_data = {
            self.gradable_task.name: [failing_solution]
        }
        result = get_passed_and_failed_tasks(solution_data)
        self.assertEqual("Failed", result.get(self.gradable_task.name))


class TestGetSolutionData(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.gradable_task = IncludedTaskFactory(topic__course=self.course, gradable=True)
        self.non_gradable_task = IncludedTaskFactory(topic__course=self.course, gradable=False)
        self.student = StudentFactory()
        add_student(course=self.course, student=self.student)

    def test_solutions_to_tasks_are_added_to_return_dict(self):
        gradable_solution = SolutionFactory(student=self.student, task=self.gradable_task, status=Solution.OK)
        non_gradable_solution = SolutionFactory(
            student=self.student, task=self.non_gradable_task, status=Solution.SUBMITTED_WITHOUT_GRADING
        )

        solution_data, _ = get_solution_data(course=self.course, student=self.student)

        self.assertEqual([gradable_solution], solution_data.get(self.gradable_task.name))
        self.assertEqual([non_gradable_solution], solution_data.get(self.non_gradable_task.name))

    def test_task_is_not_added_as_key_if_no_solutions_for_it(self):
        solution_data, _ = get_solution_data(course=self.course, student=self.student)

        self.assertIsNone(solution_data.get(self.gradable_task.name))


class TestGetAllSolvedStudentSolutionCountForCourse(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.gradable_task = IncludedTaskFactory(topic__course=self.course, gradable=True)
        self.non_gradable_task = IncludedTaskFactory(topic__course=self.course, gradable=False)
        self.student = StudentFactory()
        add_student(course=self.course, student=self.student)

    def test_correct_count_is_returned_when_student_has_passing_solutions(self):
        SolutionFactory(student=self.student, task=self.gradable_task, status=Solution.OK)
        SolutionFactory(
            student=self.student, task=self.non_gradable_task, status=Solution.SUBMITTED_WITHOUT_GRADING
        )

        students_passed_solution_count = get_all_solved_student_solution_count_for_course(course=self.course)

        self.assertEqual(2, students_passed_solution_count.get(self.student.email))

    def test_student_is_not_present_in_result_if_has_no_passing_solutions(self):
        SolutionFactory(student=self.student, task=self.gradable_task, status=Solution.NOT_OK)
        students_passed_solution_count = get_all_solved_student_solution_count_for_course(course=self.course)

        self.assertIsNone(students_passed_solution_count.get(self.student.email))

    def test_student_is_not_present_in_result_if_has_no_solutions(self):
        students_passed_solution_count = get_all_solved_student_solution_count_for_course(course=self.course)

        self.assertIsNone(students_passed_solution_count.get(self.student.email))
