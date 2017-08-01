from django.views.generic import FormView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.conf import settings
from django.http import Http404

from odin.common.services import send_email
from odin.education.mixins import CourseViewMixin, CallServiceMixin
from odin.education.permissions import IsTeacherInCoursePermission
from .models import Application
from .forms import ApplicationInfoModelForm, IncludedApplicationTaskForm, ApplicationCreateForm, ApplicationEditForm
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
    ApplicationTasksMixin
)


class CreateApplicationInfoView(CourseViewMixin,
                                LoginRequiredMixin,
                                IsTeacherInCoursePermission,
                                ApplicationInfoFormDataMixin,
                                CallServiceMixin,
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


class EditApplicationInfoView(CourseViewMixin,
                              LoginRequiredMixin,
                              IsTeacherInCoursePermission,
                              ApplicationInfoFormDataMixin,
                              UpdateView):

    form_class = ApplicationInfoModelForm
    template_name = "applications/create_application_info.html"

    def get_object(self):
        return self.course.application_info

    def get_success_url(self):
        success_url = reverse_lazy('dashboard:education:user-course-detail',
                                   kwargs={'course_id': self.course.id})

        return success_url


class CreateIncludedApplicationTaskView(CourseViewMixin,
                                        LoginRequiredMixin,
                                        IsTeacherInCoursePermission,
                                        CallServiceMixin,
                                        FormView):
    form_class = IncludedApplicationTaskForm
    template_name = "applications/add_task.html"

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            post_data = self.request.POST
            data = {}
            data['name'] = post_data.get('name')
            data['description'] = post_data.get('description')
            data['existing_task'] = post_data.get('existing_task')
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


class ApplyToCourseView(CourseViewMixin,
                        LoginRequiredMixin,
                        ApplicationFormDataMixin,
                        HasStudentAlreadyAppliedMixin,
                        CallServiceMixin,
                        FormView):

    form_class = ApplicationCreateForm
    template_name = "applications/course_application.html"
    success_url = reverse_lazy('dashboard:applications:user-applications')

    def form_valid(self, form):
        instance = self.call_service(service=create_application, service_kwargs=form.cleaned_data)

        if instance:
            template_name = settings.EMAIL_TEMPLATES.get('application_completed_default')
            context = {
                'user': self.request.user.email,
                'course': self.course.name
            }
            send_email(template_name=template_name, recipients=[self.request.user.email], context=context)
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


class EditApplicationView(CourseViewMixin,
                          ApplicationTasksMixin,
                          LoginRequiredMixin,
                          ApplicationFormDataMixin,
                          CallServiceMixin,
                          UpdateView):
    form_class = ApplicationEditForm
    template_name = "applications/edit_application.html"
    success_url = reverse_lazy('dashboard:applications:user-applications')

    def get_object(self):
        user_application = self.request.user.applications.filter(application_info=self.course.application_info)
        if user_application.exists():
            return user_application.first()
        raise Http404

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
