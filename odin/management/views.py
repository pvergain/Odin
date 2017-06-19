from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from .permissions import DashboardManagementPermission
from .forms import ManagementAddUserForm
from .filters import UserFilter


from odin.users.models import BaseUser
from odin.users.services import create_user

from odin.education.models import Student, Teacher


class DashboardManagementView(LoginRequiredMixin,
                              DashboardManagementPermission,
                              ListView):
    template_name = 'dashboard/management.html'
    paginate_by = 100
    filter_class = UserFilter
    queryset = BaseUser.objects.select_related('profile').all()\
        .prefetch_related('student', 'teacher').order_by('-id')

    def get_queryset(self):
        self.filter = self.filter_class(self.request.GET, queryset=self.queryset)
        return self.filter.qs


class MakeStudentOrTeacherView(LoginRequiredMixin,
                               DashboardManagementPermission,
                               View):
    def get(self, request, *args, **kwargs):
        if self.kwargs.get('type') == 'teacher':
            user = BaseUser.objects.get(id=kwargs.get('id'))
            Teacher.objects.create_from_user(user)
        elif self.kwargs.get('type') == 'student':
            user = BaseUser.objects.get(id=kwargs.get('id'))
            Student.objects.create_from_user(user)
        else:
            return Http404
        return redirect(reverse_lazy('dashboard:management:management_index'))


class ManagementUserCreateView(LoginRequiredMixin,
                               DashboardManagementPermission,
                               FormView):
    form_class = ManagementAddUserForm
    template_name = 'dashboard/add_user.html'
    success_url = reverse_lazy('dashboard:management:management_index')

    def form_valid(self, form):
        instance = create_user(**form.cleaned_data)

        if self.request.GET.get('type') == 'students':
            Student.objects.create_from_user(instance)
        elif self.request.GET.get('type') == 'teachers':
            Teacher.objects.create_from_user(instance)

        return super().form_valid(form)
