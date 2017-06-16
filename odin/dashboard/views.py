from django.views.generic import TemplateView, RedirectView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .mixins import ManagementDashboardPermissionMixin

from odin.users.models import BaseUser
from odin.education.models import Student, Teacher


class RedirectToDashboardIndexView(RedirectView):
    url = reverse_lazy('dashboard:index')


class DashboardIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'


class DashboardManagementView(ManagementDashboardPermissionMixin, ListView):
    template_name = 'dashboard/management.html'
    paginate_by = 100

    def get_queryset(self):
        if self.request.GET.get('filter', None) == 'students':
            return Student.objects.select_related('profile').all()
        elif self.request.GET.get('filter', None) == 'teachers':
            return Teacher.objects.select_related('profile').all()

        return BaseUser.objects.select_related('profile').all()
