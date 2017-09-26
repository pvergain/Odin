from django.http import Http404

from .models import Competition


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
