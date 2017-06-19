from django.shortcuts import redirect
from django.views.generic import View, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from .permissions import DashboardManagementPermission
from .filters import UserFilter
from .mixins import DashboardCreateUserMixin

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


class PromoteUserToStudentView(LoginRequiredMixin,
                               DashboardManagementPermission,
                               View):
    def get(self, request, *args, **kwargs):
        instance = BaseUser.objects.get(id=kwargs.get('id'))
        Student.objects.create_from_user(instance)
        return redirect('dashboard:management:management_index')


class PromoteUserToTeacherView(LoginRequiredMixin,
                               DashboardManagementPermission,
                               View):
    def get(self, request, *args, **kwargs):
        instance = BaseUser.objects.get(id=kwargs.get('id'))
        Teacher.objects.create_from_user(instance)
        return redirect('dashboard:management:management_index')


class CreateUserView(DashboardCreateUserMixin, FormView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'user'
        return context

    def form_valid(self, form):
        create_user(**form.cleaned_data)

        return super().form_valid(form)


class CreateStudentView(DashboardCreateUserMixin, FormView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'student'
        return context

    def form_valid(self, form):
        instance = create_user(**form.cleaned_data)

        Student.objects.create_from_user(instance)
        return super().form_valid(form)


class CreateTeacherView(DashboardCreateUserMixin, FormView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'teacher'
        return context

    def form_valid(self, form):
        instance = create_user(**form.cleaned_data)

        Teacher.objects.create_from_user(instance)
        return super().form_valid(form)
