from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .permissions import DashboardManagementPermission
from .forms import ManagementAddUserForm


class DashboardCreateUserMixin(LoginRequiredMixin, DashboardManagementPermission):
    form_class = ManagementAddUserForm
    template_name = 'dashboard/add_user.html'
    success_url = reverse_lazy('dashboard:management:index')
