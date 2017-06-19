from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from .permissions import DashboardManagementPermission
from .forms import ManagementAddUserForm


from odin.users.models import BaseUser
from odin.users.services import create_user

from odin.education.models import Student, Teacher


class DashboardManagementView(LoginRequiredMixin,
                              DashboardManagementPermission,
                              ListView):
    template_name = 'dashboard/management.html'
    paginate_by = 100

    def get_queryset(self):
        queryset = BaseUser.objects.select_related('profile').all()\
            .prefetch_related('student', 'teacher').order_by('-id')
        if self.request.GET.get('filter', None) == 'students':
            return queryset.filter(student__isnull=False)
        elif self.request.GET.get('filter', None) == 'teachers':
            return queryset.filter(teacher__isnull=False)
        return queryset


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

        if self.request.GET.get('filter') == 'students':
            Student.objects.create_from_user(instance)
        elif self.request.GET.get('filter') == 'teachers':
            Teacher.objects.create_from_user(instance)

        return super().form_valid(form)
