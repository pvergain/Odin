from rest_framework import generics

from django.contrib.auth.mixins import LoginRequiredMixin

from odin.common.mixins import CallServiceMixin
from odin.grading.services import start_grader_communication

from .mixins import CompetitionViewMixin, CreateSolutionApiMixin
from .permissions import IsParticipantInCompetitionApiPerimission, IsParticipantOrJudgeInCompetitionApiPermission
from .serializers import CompetitionSolutionSerializer
from .services import create_gradable_solution, create_non_gradable_solution
from .models import Solution


class CreateGradableSolutionApiView(LoginRequiredMixin,
                                    CompetitionViewMixin,
                                    CreateSolutionApiMixin,
                                    CallServiceMixin,
                                    generics.CreateAPIView):
    serializer_class = CompetitionSolutionSerializer
    permission_classes = (IsParticipantInCompetitionApiPerimission, )

    def get_service(self):
        return create_gradable_solution

    def perform_create(self, serializer):
        service_kwargs = serializer.validated_data
        solution = self.call_service(service_kwargs=service_kwargs)

        if solution:
            serializer.instance = solution
            start_grader_communication(solution.id, 'competitions.Solution')


class CreateNonGradableSolutionApiView(LoginRequiredMixin,
                                       CompetitionViewMixin,
                                       CreateSolutionApiMixin,
                                       CallServiceMixin,
                                       generics.CreateAPIView):
    serializer_class = CompetitionSolutionSerializer
    permission_classes = (IsParticipantInCompetitionApiPerimission, )

    def get_service(self):
        return create_non_gradable_solution

    def perform_create(self, serializer):
        service_kwargs = serializer.validated_data
        solution = self.call_service(service_kwargs=service_kwargs)

        if solution:
            serializer.instance = solution


class SolutionDetailApiView(generics.RetrieveAPIView):
    serializer_class = CompetitionSolutionSerializer
    permission_classes = (IsParticipantOrJudgeInCompetitionApiPermission, )
    queryset = Solution.objects.all()
    lookup_url_kwarg = 'solution_id'
