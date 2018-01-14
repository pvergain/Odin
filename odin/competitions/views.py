from django.views.generic import View
from django.shortcuts import redirect

from rest_framework import serializers

from odin.applications.models import Application

from odin.competitions.models import CompetitionTask
from odin.competitions.services import update_application_competition_solutions


TASK_KEY = 'task_'


def is_task_key(key):
    return key.startswith(TASK_KEY)


def parse_task_key(key):
    return int(key[len(TASK_KEY):])


class UpdateApplicationCompetitionSolutionsView(View):
    class ViewSerializer(serializers.Serializer):
        application = serializers.PrimaryKeyRelatedField(
           queryset=Application.objects.all()
        )

    def post(self, request):
        serializer = self.ViewSerializer(data=request.POST)
        serializer.is_valid()

        task_to_solutions = {}

        for key, value in request.POST.items():
            if is_task_key(key):
                task_id = parse_task_key(key)
                task_to_solutions[CompetitionTask.objects.get(id=task_id)] = value

        application = serializer.validated_data['application']

        update_application_competition_solutions(
            application=application,
            task_to_solutions=task_to_solutions,
            participant=request.user
        )

        return redirect(
            'dashboard:applications:edit',
            course_slug=application.application_info.course.slug_url
        )
