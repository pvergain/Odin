"""
TO DO write test for get_grader_ready_data

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

"""
