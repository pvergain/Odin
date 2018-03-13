import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from odin.education.apis.services import (
    get_all_course_assignments_per_student,
    get_gradable_tasks_per_course,
    get_all_topics_for_courses_of_a_student
)

from odin.education.services import create_gradable_solution
from odin.grading.services import start_grader_communication
from django.shortcuts import get_object_or_404

from odin.education.models import IncludedTask, Solution

'''
Create your views here
'''


class JSONWebTokenAuthenticationMixin:
    authentication_classes = (JSONWebTokenAuthentication,)
    permissions_classes = (IsAuthenticated, )


class MainView(JSONWebTokenAuthenticationMixin, APIView):
    def get(self, request, task_id=None):
        if not task_id:
            assignments = get_all_course_assignments_per_student(student=self.request.user.student)
            gradable_tasks = get_gradable_tasks_per_course(all_topics=get_all_topics_for_courses_of_a_student(
                                                                      course_assignments_per_student=assignments))
            data = json.dumps(gradable_tasks)

            return Response(data)
        else:
            return Response({'task_id': task_id})

    def post(self, request):
        create_gradable_solution_kwargs = {
            'student': self.request.user.student,
            'task': get_object_or_404(IncludedTask, id=self.request.POST['task_id']),
            'code': self.request.POST['code']
        }
        solution = create_gradable_solution(**create_gradable_solution_kwargs)
        if solution:
            start_grader_communication(solution.id, 'education.Solution')
            return Response({'solution_id': solution.id})
        else:
            return Response({'problem': 'error occured'})


class SolutionStatusView(JSONWebTokenAuthenticationMixin, APIView):
    def get(self, request, *args, **kwargs):
        solution_id = kwargs['solution_id']
        solution = get_object_or_404(Solution, id=solution_id)
        if solution:
            return Response({"solution_id": solution_id, "solution_status": solution.STATUS_CHOICE[solution.status]})

    def post(self, request):
        return Response({"error": "nothing here"})
