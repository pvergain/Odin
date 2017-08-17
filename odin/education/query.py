from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone

from odin.users.models import BaseUser


class TaskQuerySet(models.QuerySet):

    def get_tasks_for(self, course, gradable=False):
        return self.filter(topic__course=course, gradable=gradable)


class SolutionQuerySet(models.QuerySet):

    def get_solutions_for(self, user, task):
        return self.filter(student=user, task=task)


class CheckInQuerySet(models.QuerySet):

    def get_user_dates(self, user, course):
        user = get_object_or_404(BaseUser, id=user.id)
        return self.filter(user=user,
                           date__gte=course.start_date,
                           date__lte=course.end_date).values_list('date', flat=True)


class CourseQuerySet(models.QuerySet):
    def get_active_courses(self):
        return self.filter(start_date__lte=timezone.now().date(),
                           end_date__gte=timezone.now().date())
