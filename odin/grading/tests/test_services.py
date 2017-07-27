from test_plus import TestCase

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from odin.common.faker import faker

from ..services import create_plain_problem, create_binary_problem
from ..models import GraderBinaryProblem, GraderPlainProblem


class TestCreatePlainProblem(TestCase):
    def setUp(self):
        self.language = 'python'
        self.test_type = GraderPlainProblem.UNITTEST
        self.file_type = GraderPlainProblem.PLAIN
        self.code = faker.text()
        self.test = faker.text()
        self.false_type = 99

    def test_create_plain_problem_raises_validation_error_when_language_not_in_supported_languages(self):
        with self.assertRaises(ValidationError):
            create_plain_problem(language='',
                                 test_type=self.test_type,
                                 file_type=self.file_type,
                                 solution=self.code,
                                 test=self.test)

    def test_create_plain_problem_raises_validation_error_when_test_type_not_in_supported_test_types(self):
        with self.assertRaises(ValidationError):
            create_plain_problem(language=self.language,
                                 test_type=self.false_type,
                                 file_type=self.file_type,
                                 solution=self.code,
                                 test=self.test)

    def test_create_plain_problem_raises_validation_error_when_file_type_not_in_supported_file_types(self):
        with self.assertRaises(ValidationError):
            create_plain_problem(language=self.language,
                                 test_type=self.test_type,
                                 file_type=self.false_type,
                                 solution=self.code,
                                 test=self.test)

    def test_create_plain_problem_creates_plain_problem_when_data_is_valid(self):
        current_count = GraderPlainProblem.objects.count()

        create_plain_problem(language=self.language,
                             test_type=self.test_type,
                             file_type=self.file_type,
                             solution=self.code,
                             test=self.test)

        self.assertEqual(current_count + 1, GraderPlainProblem.objects.count())


class TestCreateBinaryProblem(TestCase):
    def setUp(self):
        self.language = 'python'
        self.test_type = GraderBinaryProblem.UNITTEST
        self.file_type = GraderBinaryProblem.BINARY
        self.code = SimpleUploadedFile('code.jar', bytes(f'{faker.text}'.encode('utf-8')))
        self.test = SimpleUploadedFile('test.jar', bytes(f'{faker.text}'.encode('utf-8')))
        self.false_type = 99

    def test_create_binary_problem_raises_validation_error_when_language_not_in_supported_languages(self):
        with self.assertRaises(ValidationError):
            create_binary_problem(language='',
                                  test_type=self.test_type,
                                  file_type=self.file_type,
                                  solution=self.code,
                                  test=self.test)

    def test_create_binary_problem_raises_validation_error_when_test_type_not_in_supported_test_types(self):
        with self.assertRaises(ValidationError):
            create_binary_problem(language=self.language,
                                  test_type=self.false_type,
                                  file_type=self.file_type,
                                  solution=self.code,
                                  test=self.test)

    def test_create_binary_problem_raises_validation_error_when_file_type_not_in_supported_file_types(self):
        with self.assertRaises(ValidationError):
            create_binary_problem(language=self.language,
                                  test_type=self.test_type,
                                  file_type=self.false_type,
                                  solution=self.code,
                                  test=self.test)

    def test_create_binary_problem_creates_binary_problem_when_data_is_valid(self):
        current_count = GraderBinaryProblem.objects.count()

        create_binary_problem(language=self.language,
                              test_type=self.test_type,
                              file_type=self.file_type,
                              solution=self.code,
                              test=self.test)

        self.assertEqual(current_count + 1, GraderBinaryProblem.objects.count())
