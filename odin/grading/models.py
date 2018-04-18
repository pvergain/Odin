from django.db import models


class GraderRequest(models.Model):
    request_info = models.CharField(max_length=255)
    nonce = models.BigIntegerField(db_index=True)
