from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView, RedirectView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

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
            return Student.objects.select_related('profile').all().order_by('-id')
        elif self.request.GET.get('filter', None) == 'teachers':
            return Teacher.objects.select_related('profile').all().order_by('-id')

        return BaseUser.objects.select_related('profile').all().prefetch_related('student', 'teacher').order_by('-id')


class MakeStudentOrTeacherView(ManagementDashboardPermissionMixin, View):
    def get(self, request, *args, **kwargs):
        if self.kwargs.get('type') == 'teacher':
            user = BaseUser.objects.get(id=kwargs.get('id'))
            Teacher.objects.create_from_user(user)
        elif self.kwargs.get('type') == 'student':
            user = BaseUser.objects.get(id=kwargs.get('id'))
            Student.objects.create_from_user(user)
        else:
            return Http404
        return redirect(reverse_lazy('dashboard:management'))
