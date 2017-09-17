from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin


class RedirectToDashboardIndexView(RedirectView):
    url = reverse_lazy('dashboard:index')


class DashboardIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'


class TempDashboardIndexView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('dashboard:education:user-courses')
