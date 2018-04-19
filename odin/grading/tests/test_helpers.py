from django.test import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from odin.common.faker import faker
from unittest.mock import patch

from odin.education.factories import (
    SolutionFactory,
    IncludedTaskFactory,
    SourceCodeTestFactory,
    BinaryFileTestFactory,
    ProgrammingLanguageFactory,
)


from odin.education.models import (
    IncludedTask,
    Solution,
)

from odin.grading.helper import get_grader_ready_data


class GradingHelperTests(TestCase):
    def setUp(self):
        self.task = IncludedTaskFactory()
        self.task.gradable = True
        self.task.save()
        self.solution = SolutionFactory(task=self.task)
        self.requirements = 'openpyxl==2.5.1\nFaker==0.8.12'

    def test_get_grader_ready_data_raises_validation_error_when_language_not_in_supported_and_test_is_source(self):
        language = ProgrammingLanguageFactory(name='c_sharp')
        SourceCodeTestFactory._create(
            IncludedTask,
            task=self.task,
            language=language
        )

        with self.assertRaises(ValidationError):
            get_grader_ready_data(
                solution_id=self.solution.id,
                solution_model=Solution,
            )

    @patch.dict('odin.grading.helper.TEST_TYPES', {'UNITTEST': faker.word()}, clear=True)
    def test_get_grader_ready_data_raises_validation_error_when_test_type_is_not_supported_and_test_is_source(self):

        language = ProgrammingLanguageFactory(name='python')
        SourceCodeTestFactory._create(
            IncludedTask,
            task=self.task,
            language=language
        )

        with self.assertRaises(ValidationError):
            get_grader_ready_data(
                solution_id=self.solution.id,
                solution_model=Solution,
            )

    @patch.dict('odin.grading.helper.FILE_TYPES', {'BINARY': faker.word()}, clear=True)
    def test_get_grader_ready_data_raises_validation_error_when_file_type_is_not_supported_and_test_is_source(self):

        language = ProgrammingLanguageFactory(name='ruby')
        SourceCodeTestFactory._create(
            IncludedTask,
            task=self.task,
            language=language
        )

        with self.assertRaises(ValidationError):
            get_grader_ready_data(
                solution_id=self.solution.id,
                solution_model=Solution,
            )

    def test_get_grader_ready_data_returns_problem_parameters_when_data_is_valid_and_test_is_source(self):
        language = ProgrammingLanguageFactory(name='java')
        SourceCodeTestFactory._create(
            IncludedTask,
            task=self.task,
            language=language
        )

        data = get_grader_ready_data(
            solution_id=self.solution.id,
            solution_model=Solution
        )

        self.assertIsInstance(data, dict)

    def test_get_grader_ready_data_raises_validation_error_when_language_is_not_supported_and_test_is_not_source(self):
        language = ProgrammingLanguageFactory(name=faker.word())
        self.solution.code = None
        self.solution.file = SimpleUploadedFile('solution.jar', bytes(f'{faker.text()}'.encode('utf-8')))
        self.solution.save()
        BinaryFileTestFactory._create(
            IncludedTask,
            task=self.task,
            language=language
        )

        with self.assertRaises(ValidationError):
            get_grader_ready_data(
                solution_id=self.solution.id,
                solution_model=Solution,
            )

    @patch.dict('odin.grading.helper.TEST_TYPES', {'OUTPUT_CHECKING': faker.word()})
    def test_get_grader_ready_data_raises_validation_error_when_test_type_is_not_supported_and_test_is_not_source(self):
        language = ProgrammingLanguageFactory(name='python')
        self.solution.code = None
        self.solution.file = SimpleUploadedFile('solution.jar', bytes(f'{faker.text()}'.encode('utf-8')))
        self.solution.save()
        BinaryFileTestFactory._create(
            IncludedTask,
            task=self.task,
            language=language
        )

        with self.assertRaises(ValidationError):
            get_grader_ready_data(
                solution_id=self.solution.id,
                solution_model=Solution,
            )

    @patch.dict('odin.grading.helper.FILE_TYPES', {'BINARY': faker.word()}, clear=True)
    def test_get_grader_ready_data_raises_validation_error_when_file_type_is_not_supported_and_test_is_not_source(self):
        language = ProgrammingLanguageFactory(name='ruby')
        self.solution.code = None
        self.solution.file = SimpleUploadedFile('solution.jar', bytes(f'{faker.text()}'.encode('utf-8')))
        self.solution.save()
        BinaryFileTestFactory._create(
            IncludedTask,
            task=self.task,
            language=language
        )

        with self.assertRaises(ValidationError):
            get_grader_ready_data(
                solution_id=self.solution.id,
                solution_model=Solution,
            )

    def test_get_grader_ready_data_return_problem_parameters_when_data_is_valid_and_test_is_not_source(self):
        language = ProgrammingLanguageFactory(name='java')
        self.solution.code = None
        self.solution.file = SimpleUploadedFile('solution.jar', bytes(f'{faker.text()}'.encode('utf-8')))
        self.solution.save()
        BinaryFileTestFactory._create(
            IncludedTask,
            task=self.task,
            language=language
        )

        data = get_grader_ready_data(
            solution_id=self.solution.id,
            solution_model=Solution
        )

        self.assertIsInstance(data, dict)

    def test_problem_contains_extra_options_when_has_requirements_when_data_is_valid_and_test_is_source(self):

        language = ProgrammingLanguageFactory(name='java')
        test = SourceCodeTestFactory._create(
            IncludedTask,
            task=self.task,
            language=language
        )
        test.requirements = self.requirements
        test.save()

        data = get_grader_ready_data(
            solution_id=self.solution.id,
            solution_model=Solution
        )

        self.assertIsInstance(data, dict)
        self.assertFalse(data['extra_options'] == {})
