from django.views.generic import FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from odin.education.mixins import CourseViewMixin, CallServiceMixin
from odin.education.permissions import IsTeacherInCoursePermission
from .forms import ApplicationInfoModelForm
from .services import create_application_info
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


class EditApplicationView(CourseViewMixin,
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
