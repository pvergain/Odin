from django.http import Http404
from django.shortcuts import get_object_or_404

from odin.common.utils import transfer_POST_data_to_dict

from .models import Competition, CompetitionTask


class CompetitionViewMixin:
    def dispatch(self, request, *args, **kwargs):
        competition_slug = self.kwargs.get('competition_slug')

        competition = Competition.objects.filter(slug_url=competition_slug)

        if competition.exists():
            self.competition = competition.first()
        else:
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['competition'] = self.competition

        return context


class CreateSolutionApiMixin:
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()

        data = transfer_POST_data_to_dict(kwargs.get('data'))
        data['task'] = get_object_or_404(CompetitionTask, id=self.kwargs.get('task_id')).id
        data['participant'] = self.request.user.competitionparticipant
        kwargs['data'] = data

        return serializer_class(*args, **kwargs)
