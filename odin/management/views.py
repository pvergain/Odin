from django.shortcuts import redirect
from django.views.generic import View, ListView, FormView
from django.urls import reverse_lazy

from odin.users.models import BaseUser
from odin.users.services import create_user

from odin.education.mixins import CallServiceMixin  # TODO: Move to common
from odin.education.models import Student, Teacher, Course
from odin.education.forms import ManagementAddCourseForm  # TODO: Check
from odin.education.services import create_course, add_student

from odin.common.mixins import ReadableFormErrorsMixin

from .permissions import DashboardManagementPermission
from .filters import UserFilter
from .mixins import DashboardCreateUserMixin
from .forms import AddStudentToCourseForm


class DashboardManagementView(DashboardManagementPermission,
                              ListView):
    template_name = 'dashboard/management.html'
    paginate_by = 101
    filter_class = UserFilter
    queryset = BaseUser.objects.select_related('profile').all()\
        .prefetch_related('student', 'teacher').order_by('-id')

    def get_queryset(self):
        self.filter = self.filter_class(self.request.GET, queryset=self.queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.prefetch_related('students', 'teachers')
        return context


class PromoteUserToStudentView(DashboardManagementPermission,
                               View):
    def get(self, request, *args, **kwargs):
        instance = BaseUser.objects.get(id=kwargs.get('id'))
        Student.objects.create_from_user(instance)
        return redirect('dashboard:management:index')


class PromoteUserToTeacherView(DashboardManagementPermission,
                               View):
    def get(self, request, *args, **kwargs):
        instance = BaseUser.objects.get(id=kwargs.get('id'))
        Teacher.objects.create_from_user(instance)
        return redirect('dashboard:management:index')


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


class CreateCourseView(DashboardManagementPermission,
                       FormView):
    template_name = 'dashboard/add_course.html'
    form_class = ManagementAddCourseForm

    def form_valid(self, form):
        course = create_course(**form.cleaned_data)
        self.course_id = course.id

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course_id})


class AddStudentToCourseView(DashboardManagementPermission,
                             CallServiceMixin,
                             ReadableFormErrorsMixin,
                             FormView):
    template_name = 'dashboard/add_student_to_course.html'
    form_class = AddStudentToCourseForm
    success_url = reverse_lazy('dashboard:management:index')

    def get_service(self):
        return add_student

    def form_valid(self, form):
        self.call_service(service_kwargs=form.cleaned_data)

        return super().form_valid(form)
