from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .mixins import ManagementDashboardPermissionMixin


class RedirectToDashboardIndexView(RedirectView):
    url = reverse_lazy('dashboard:index')


class DashboardIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'


class DashboardManagementView(ManagementDashboardPermissionMixin, TemplateView):
    template_name = 'dashboard/management.html'
