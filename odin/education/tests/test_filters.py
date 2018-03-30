from test_plus import TestCase

from odin.common.faker import faker

from ..models import IncludedTask, Solution
from ..factories import IncludedTaskFactory, CourseFactory, SolutionFactory, WeekFactory
from ..filters import SolutionsFilter


class TestSolutionFilter(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.week = WeekFactory(course=self.course)
        self.task = IncludedTaskFactory(course=self.course, week=self.week, gradable=True)
        self.filter = SolutionsFilter(task=self.task)
        self.queryset = IncludedTask.objects.all()

    def test_filter_outputs_no_correct_solution_if_there_are_none(self):
        name = faker.name()
        self.assertEqual([], list(self.filter.filter_solutions(self.queryset, name, 'correct')))

    def test_filter_outputs_correct_solutions_when_they_exist(self):
        SolutionFactory(task=self.task, status=Solution.OK)
        name = faker.name()
        self.assertEqual([self.task], list(self.filter.filter_solutions(self.queryset, name, 'correct')))
