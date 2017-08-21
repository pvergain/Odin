from django.views.generic import FormView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from odin.common.utils import transfer_POST_data_to_dict
from odin.common.mixins import CallServiceMixin, ReadableFormErrorsMixin
from odin.education.mixins import CourseViewMixin
from odin.education.models import Course
from odin.education.permissions import IsTeacherInCoursePermission
from odin.interviews.permissions import IsInterviewerPermission
from .models import Application, ApplicationTask
from .forms import (
    ApplicationInfoModelForm,
    IncludedApplicationTaskForm,
    ApplicationCreateForm,
    ApplicationEditForm,
    IncludedApplicationTaskFromExistingForm
)
from .services import (
    create_application_info,
    create_included_application_task,
    create_application,
    create_application_solution
)
from .mixins import (
    ApplicationInfoFormDataMixin,
    HasStudentAlreadyAppliedMixin,
    ApplicationFormDataMixin,
    ApplicationTasksMixin,
    RedirectToExternalFormMixin
)


class CreateApplicationInfoView(LoginRequiredMixin,
                                CourseViewMixin,
                                IsTeacherInCoursePermission,
                                ApplicationInfoFormDataMixin,
                                CallServiceMixin,
                                ReadableFormErrorsMixin,
                                FormView):
    form_class = ApplicationInfoModelForm
    template_name = "applications/create_application_info.html"

    def form_valid(self, form):
        self.call_service(service=create_application_info, service_kwargs=form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy('dashboard:education:user-course-detail',
                                   kwargs={'course_id': self.course.id})

        return success_url


class EditApplicationInfoView(LoginRequiredMixin,
                              CourseViewMixin,
                              IsTeacherInCoursePermission,
                              ApplicationInfoFormDataMixin,
                              ReadableFormErrorsMixin,
                              UpdateView):

    form_class = ApplicationInfoModelForm
    template_name = "applications/create_application_info.html"

    def get_object(self):
        return self.course.application_info

    def get_success_url(self):
        success_url = reverse_lazy('dashboard:education:user-course-detail',
                                   kwargs={'course_id': self.course.id})

        return success_url


class AddIncludedApplicationTaskFromExistingView(LoginRequiredMixin,
                                                 CourseViewMixin,
                                                 IsTeacherInCoursePermission,
                                                 CallServiceMixin,
                                                 ReadableFormErrorsMixin,
                                                 FormView):
    template_name = "applications/existing_task_list.html"
    form_class = IncludedApplicationTaskFromExistingForm

    def get_success_url(self):
        success_url = reverse_lazy('dashboard:applications:edit-application-info',
                                   kwargs={'course_id': self.course.id})
        return success_url

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST, PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['application_info'] = self.course.application_info.id
            form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        data = {
            'existing_task': form.cleaned_data.get('task'),
            'application_info': form.cleaned_data.get('application_info')
        }
        self.call_service(service=create_included_application_task, service_kwargs=data)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_list'] = ApplicationTask.objects.all()
        return context


class CreateIncludedApplicationTaskView(LoginRequiredMixin,
                                        CourseViewMixin,
                                        IsTeacherInCoursePermission,
                                        CallServiceMixin,
                                        ReadableFormErrorsMixin,
                                        FormView):
    form_class = IncludedApplicationTaskForm
    template_name = "applications/add_task.html"

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['application_info'] = self.course.application_info.id

            form_kwargs['data'] = data
        return form_kwargs

    def get_success_url(self):
        success_url = reverse_lazy('dashboard:applications:edit-application-info',
                                   kwargs={'course_id': self.course.id})
        return success_url

    def form_valid(self, form):
        self.call_service(service=create_included_application_task, service_kwargs=form.cleaned_data)
        return super().form_valid(form)


class ApplyToCourseView(LoginRequiredMixin,
                        CourseViewMixin,
                        RedirectToExternalFormMixin,
                        ApplicationFormDataMixin,
                        HasStudentAlreadyAppliedMixin,
                        CallServiceMixin,
                        ReadableFormErrorsMixin,
                        FormView):

    form_class = ApplicationCreateForm
    template_name = "applications/course_application.html"
    success_url = reverse_lazy('dashboard:applications:user-applications')

    def form_valid(self, form):
        self.call_service(service=create_application, service_kwargs=form.cleaned_data)

        return super().form_valid(form)


class UserApplicationsListView(LoginRequiredMixin,
                               ListView):
    template_name = 'applications/user_applications_list.html'

    def get_queryset(self):
        prefetch = [
            'application_info__course',
            'application_info__tasks',
        ]

        return Application.objects.filter(user=self.request.user).prefetch_related(*prefetch)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_teacher():
            teacher = self.request.user.teacher
            prefetch = [
                'application_info__applications__user__profile',
                'application_info__tasks',
            ]
            filters = {
                'teachers__in': [teacher]
            }

            courses = Course.objects.get_active_for_interview().filter(**filters)
            context['teached_courses'] = courses.prefetch_related(*prefetch).order_by('-start_date')

        return context


class EditApplicationView(LoginRequiredMixin,
                          CourseViewMixin,
                          ApplicationTasksMixin,
                          ApplicationFormDataMixin,
                          CallServiceMixin,
                          ReadableFormErrorsMixin,
                          UpdateView):
    form_class = ApplicationEditForm
    template_name = "applications/edit_application.html"
    success_url = reverse_lazy('dashboard:applications:user-applications')

    def get_object(self):
        user_application = get_object_or_404(Application, user=self.request.user, application_info__course=self.course)
        return user_application

    def get_initial(self):
        initial = super().get_initial()
        if hasattr(self.object, 'solutions'):
            for task in self.application_tasks:
                solution = self.object.solutions.filter(task=task)
                if solution.exists():
                    initial[task.name] = solution.first().url
        return initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            post_data = self.request.POST
            for task in self.application_tasks:
                form_kwargs['data'][task.name] = post_data.get(task.name)

        return form_kwargs

    def form_valid(self, form):
        for task in self.application_tasks:
            create_solution_kwargs = {
                'task': task,
                'application': self.object,
                'url': form.cleaned_data.get(task.name)
            }
            if create_solution_kwargs['url']:
                self.call_service(service=create_application_solution, service_kwargs=create_solution_kwargs)

        return super().form_valid(form)


class ApplicationDetailView(LoginRequiredMixin,
                            IsInterviewerPermission,
                            DetailView):
    model = Application
    template_name = 'applications/application_detail.html'
    pk_url_kwarg = 'application_id'
