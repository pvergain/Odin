from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from odin.management.permissions import DashboardManagementPermission

from .mixins import CompetitionViewMixin
from .permissions import IsParticipantOrJudgeInCompetitionPermission, IsJudgeInCompetitionPermisssion
from .models import Competition


class CompetitionDetailView(LoginRequiredMixin,
                            IsParticipantOrJudgeInCompetitionPermission,
                            CompetitionViewMixin,
                            TemplateView):
    template_name = 'competitions/competition_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class CreateCompetitionView(DashboardManagementPermission,
                            CreateView):
    template_name = 'competitions/create_competition.html'
    model = Competition
    fields = ['name', 'start_date', 'end_date', 'slug_url']

    def get_success_url(self):
        return reverse_lazy('competitions:competition-detail',
                            kwargs={
                                'competition_slug': self.object.slug_url
                            })


class EditCompetitionView(LoginRequiredMixin,
                          IsJudgeInCompetitionPermisssion,
                          UpdateView):
    template_name = 'competitions/create_competition.html'

    model = Competition
    slug_field = 'slug_url'
    slug_url_kwarg = 'competition_slug'

    def get_success_url(self):
        return reverse_lazy('competitions:competition-detail',
                            kwargs={
                                'competition_slug': self.object.slug_url
                            })
