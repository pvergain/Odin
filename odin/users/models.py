import uuid

from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from image_cropping.fields import ImageRatioField, ImageCropField

from odin.common.utils import json_field_default
from odin.common.models import (
    UpdatedAtCreatedAtModelMixin,
    VoidedModelMixin,
)

from .managers import UserManager


class BaseUser(PermissionsMixin,
               UpdatedAtCreatedAtModelMixin,
               AbstractBaseUser):
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    secret_key = models.UUIDField(default=uuid.uuid4, unique=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def downcast(self, t):
        """
        Since we don't know if the given field is present,
        We cannot refresh from db with it.
        That's why we fetch a fresh object.
        """
        user = BaseUser.objects.get(id=self.id)
        prop = t.__name__.lower()

        relations = [f.name for f in BaseUser._meta.get_fields()
                     if f.many_to_one or f.one_to_one]

        if prop not in relations:
            raise ValueError(f'Cannot downcast to {prop}. Choices are {relations}')

        if hasattr(user, prop):
            return getattr(user, prop)

    def get_full_name(self):
        return self.profile.full_name

    def get_short_name(self):
        return self.get_full_name()

    def get_description(self):
        return self.profile.description

    @property
    def name(self):
        return self.get_full_name()

    def __str__(self):
        return f'{self.email}'

    def is_student(self):
        return hasattr(self, 'student')

    def is_teacher(self):
        return hasattr(self, 'teacher')

    def is_interviewer(self):
        return hasattr(self, 'interviewer')

    def rotate_secret_key(self):
        self.secret_key = uuid.uuid4()
        self.save()


class Profile(models.Model):
    user = models.OneToOneField(BaseUser)

    full_name = models.CharField(blank=True, max_length=255)
    description = models.TextField(blank=True, null=True)

    social_accounts = JSONField(default=json_field_default, blank=True, null=True)

    works_at = models.CharField(blank=True, null=True, max_length=255)
    studies_at = models.CharField(blank=True, null=True, max_length=255)

    avatar = ImageCropField(blank=True, null=True)
    full_image = ImageCropField(upload_to='avatars/', blank=True, null=True)
    cropping = ImageRatioField('full_image', '300x300')
    skype = models.CharField(blank=True, null=True, max_length=255)

    def get_gh_profile_url(self):
        return self.social_accounts.get('GitHub')


class PasswordResetToken(UpdatedAtCreatedAtModelMixin, VoidedModelMixin, models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user = models.ForeignKey(BaseUser, related_name='password_reset_tokens')

    used_at = models.DateTimeField(null=True, blank=True)

    def use(self):
        self.used_at = timezone.now()
        self.save()

    @property
    def used(self):
        return self.used_at is not None
