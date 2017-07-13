from django.db import models


class GraderRequest(models.Model):
    request_info = models.CharField(max_length=140)
    nonce = models.BigIntegerField(db_index=True)
