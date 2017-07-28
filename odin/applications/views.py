from django.views.generic import FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from odin.education.mixins import CourseViewMixin, CallServiceMixin
from odin.education.permissions import IsTeacherInCoursePermission
from .forms import ApplicationInfoModelForm, IncludedApplicationTaskForm
from .services import create_application_info, create_included_application_task
from .mixins import ApplicationInfoFormDataMixin


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
