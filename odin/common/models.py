from django.utils import timezone
from django.db import models


class UpdatedAtCreatedAtModelMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class VoidedModelMixin(models.Model):
    voided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def voided(self):
        return bool(self.voided_at)

    def void(self):
        self.voided_at = timezone.now()
        self.save()
