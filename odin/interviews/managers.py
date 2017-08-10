from django.db import models
from django.core.exceptions import ValidationError
from django.apps import apps

from odin.users.models import BaseUser

from .query import InterviewQuerySet


class InterviewerManager(models.Manager):
    def create_from_user(self, user: BaseUser):
        Interviewer = apps.get_model('interviews', 'Interviewer')
        if user.downcast(Interviewer) is not None:
            raise ValidationError('Interviewer already exists')

        user._state.adding = False

        if not user.is_active:
            user.is_active = True
            user.save()

        interviewer = Interviewer(user_id=user.id)
        interviewer.__dict__.update(user.__dict__)
        interviewer.is_staff = True

        interviewer.save()

        return Interviewer.objects.get(id=interviewer.id)


class InterviewManager(models.Manager):
    def get_queryset(self):
        return InterviewQuerySet(self.model, using=self.db)

    def get_active(self, user):
        return [interview for interview in self.get_queryset().confirmed_interviews_on(user)
                if interview.active_data()]
