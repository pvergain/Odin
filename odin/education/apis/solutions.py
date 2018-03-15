from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response

from odin.authentication.apis.permissions import JSONWebTokenAuthenticationMixin

from odin.education.models import Solution, IncludedTask
from odin.education.services import create_gradable_solution

from odin.grading.services import start_grader_communication


class SolutionSubmitApi(JSONWebTokenAuthenticationMixin, APIView):
    def get(self, request, *args, **kwargs):
        solution_id = kwargs['solution_id']
        solution = get_object_or_404(Solution, id=solution_id)
        if solution:
            return Response({"solution_id": solution_id, "solution_status": solution.STATUS_CHOICE[solution.status]})

    def post(self, request):
        if self.request.POST:
            create_gradable_solution_kwargs = {
                'student': self.request.user.student,
                'task': get_object_or_404(IncludedTask, id=self.request.POST['task_id']),
                'code': self.request.POST['code']
            }
        else:
            create_gradable_solution_kwargs = {
                'student': self.request.user.student,
                'task': get_object_or_404(IncludedTask, id=self.request.data['task_id']),
                'code': self.request.data['code']
            }
        solution = create_gradable_solution(**create_gradable_solution_kwargs)
        if solution:
            start_grader_communication(solution.id, 'education.Solution')
            return Response({'solution_id': solution.id})
        else:
            return Response({'problem': 'error occured'})
