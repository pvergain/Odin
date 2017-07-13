
import base64

from django.db import models
from django.contrib.postgres.fields import JSONField

from odin.common.utils import json_field_default


class GraderRequest(models.Model):
    request_info = models.CharField(max_length=140)
    nonce = models.BigIntegerField(db_index=True)


class GraderPlainProblem(models.Model):
    test_type = models.CharField(max_length=255, default="unittest")
    language = models.CharField(max_length=255)
    file_type = models.CharField(max_length=255, default='plain')
    code = models.TextField(null=True, blank=True)
    test = models.TextField(null=True, blank=True)
    extra_options = JSONField(blank=True, null=True, default=json_field_default())


class GraderBinaryProblem(models.Model):
    test_type = models.CharField(max_length=255, default="unittest")
    language = models.CharField(max_length=255)
    file_type = models.CharField(max_length=255, default='binary')
    code = models.FileField(upload_to="solutions", null=True, blank=True)
    test = models.FileField(upload_to="solutions", null=True, blank=True)
    extra_options = JSONField(blank=True, null=True, default=json_field_default())

    def read_binary_file(self):
        with open(self.code.file.path, 'rb') as f:
            encoded = base64.b64encode(f.read())

        return encoded.decode('ascii')

    def read_binary_test(self):
        with open(self.test.file.path, 'rb') as f:
            encoded = base64.b64encode(f.read())

        return encoded.decode('ascii')
