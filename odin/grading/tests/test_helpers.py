from django.test import TestCase

from odin.education.factories import (
    SolutionFactory,
    IncludedTaskFactory,
    SourceCodeTestFactory,
    ProgrammingLanguageFactory
)

from odin.education.models import (
    IncludedTask,
    Solution,
)

from odin.grading.helper import (
    get_grader_ready_data,
    get_grader_ready_data1,
)


class GradingHelperTests(TestCase):
    def setUp(self):
        self.task = IncludedTaskFactory()
        self.task.gradable = True
        self.task.save()
        self.solution = SolutionFactory(task=self.task)
        self.language = ProgrammingLanguageFactory(name='python')
        self.source_test = SourceCodeTestFactory._create(
            IncludedTask,
            task=self.task,
            language=self.language
        )

    def test_get_grader_ready_data_and_get_grader_data1_return_same_result_with_requirements(self):

        self.source_test.requirements = 'openpyxl==2.5.1\nFaker==0.8.12'
        self.source_test.save()

        data = get_grader_ready_data(
            solution_id=self.solution.id,
            solution_model=Solution,
        )

        data1 = get_grader_ready_data1(
            solution_id=self.solution.id,
            solution_model=Solution,
        )

        self.assertEqual(data1['solution'], data['solution'])
        self.assertEqual(data1['test'], data['test'])
        self.assertEqual(data1['test_type'], data['test_type'])
        self.assertEqual(data1['file_type'], data['file_type'])
        self.assertEqual(data1['extra_options'], data['extra_options'])

    def test_get_grader_ready_data_and_get_grader_data1_return_same_result_without_requirements(self):

        data = get_grader_ready_data(
            solution_id=self.solution.id,
            solution_model=Solution,
        )

        data1 = get_grader_ready_data1(
            solution_id=self.solution.id,
            solution_model=Solution,
        )

        self.assertEqual(data1['solution'], data['solution'])
        self.assertEqual(data1['test'], data['test'])
        self.assertEqual(data1['test_type'], data['test_type'])
        self.assertEqual(data1['extra_options'], data['extra_options'])
