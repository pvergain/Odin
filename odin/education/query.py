from django.db import models


class TaskQuerySet(models.QuerySet):

    def get_tasks_for(self, course, gradable=False):
        return self.filter(topic__course=course,
                           gradable=gradable)
