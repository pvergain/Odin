from django.db import models


class TaskQuerySet(models.QuerySet):

    def get_tasks_for(self, course):
        return self.filter(topic__course=course)


class SolutionQuerySet(models.QuerySet):

    def get_solutions_for(self, user, task):
        return self.filter(student=user, task=task)
