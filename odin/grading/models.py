
import base64

from django.db import models
from django.contrib.postgres.fields import JSONField

from odin.common.utils import json_field_default
from .mixins import GraderReadableTypesMixin


class GraderRequest(models.Model):
    request_info = models.CharField(max_length=255)
    nonce = models.BigIntegerField(db_index=True)


class GraderPlainProblem(GraderReadableTypesMixin, models.Model):
    UNITTEST = 0
    OUTPUT_CHECKING = 1

    TEST_TYPE_CHOICE = [
        (UNITTEST, 'unittest'),
        (OUTPUT_CHECKING, 'output_checking')
    ]

    PLAIN = 0

    FILE_TYPE_CHOICE = [
        (PLAIN, 'plain')
    ]

    test_type = models.SmallIntegerField(choices=TEST_TYPE_CHOICE, default=UNITTEST)
    language = models.CharField(max_length=255)
    file_type = models.SmallIntegerField(choices=FILE_TYPE_CHOICE, default=PLAIN)
    solution = models.TextField(null=True, blank=True)
    test = models.TextField(null=True, blank=True)
    extra_options = JSONField(blank=True, null=True, default=json_field_default())

    def encode_solution_text(self):
        return base64.b64encode(self.solution.encode('utf-8')).decode('ascii')

    def encode_test_text(self):
        return base64.b64encode(self.test.encode('utf-8')).decode('ascii')


class GraderBinaryProblem(GraderReadableTypesMixin, models.Model):
    UNITTEST = 0
    OUTPUT_CHECKING = 1

    TEST_TYPE_CHOICE = [
        (UNITTEST, 'unittest'),
        (OUTPUT_CHECKING, 'output_checking')
    ]

    BINARY = 0

    FILE_TYPE_CHOICE = [
        (BINARY, 'binary')
    ]

    test_type = models.SmallIntegerField(choices=TEST_TYPE_CHOICE, default=OUTPUT_CHECKING)
    language = models.CharField(max_length=255)
    file_type = models.SmallIntegerField(choices=FILE_TYPE_CHOICE, default=BINARY)
    solution = models.FileField(upload_to="solutions", null=True, blank=True)
    test = models.FileField(upload_to="solutions", null=True, blank=True)
    extra_options = JSONField(blank=True, null=True, default=json_field_default())

    def read_binary_file(self):
        encoded = base64.b64encode(self.solution.file.read())

        return encoded.decode('ascii')

    def read_binary_test(self):
        encoded = base64.b64encode(self.test.file.read())

        return encoded.decode('ascii')


class GraderPlainProblemWithRequirements(GraderReadableTypesMixin, models.Model):
    UNITTEST = 0
    OUTPUT_CHECKING = 1

    TEST_TYPE_CHOICE = [
        (UNITTEST, 'unittest'),
        (OUTPUT_CHECKING, 'output_checking')
    ]

    BINARY = 0

    FILE_TYPE_CHOICE = [
        (BINARY, 'binary')
    ]

    test_type = models.SmallIntegerField(choices=TEST_TYPE_CHOICE, default=UNITTEST)
    language = models.CharField(max_length=255)
    file_type = models.SmallIntegerField(choices=FILE_TYPE_CHOICE, default=BINARY)
    solution = models.TextField(null=True, blank=True)
    test = models.TextField(null=True, blank=True)
    extra_options = JSONField(blank=True, null=True, default=json_field_default())

    def encode_solution_text(self):
        return base64.b64encode(self.solution.encode('utf-8')).decode('ascii')

    def return_encoded_test(self):
        return self.test
