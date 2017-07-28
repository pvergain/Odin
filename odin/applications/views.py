from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from odin.education.mixins import CourseViewMixin, CallServiceMixin
from odin.education.permissions import IsTeacherInCoursePermission
from .forms import ApplicationInfoModelForm
from .services import create_application_info


class CreateApplicationInfoView(CourseViewMixin,
                                LoginRequiredMixin,
                                IsTeacherInCoursePermission,
                                CallServiceMixin,
                                FormView):
    form_class = ApplicationInfoModelForm
    template_name = "applications/create_application_info.html"

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            post_data = self.request.POST
            data = {}
            data['start_date'] = post_data.get('start_date')
            data['end_date'] = post_data.get('end_date')
            data['start_interview_date'] = post_data.get('start_interview_date')
            data['end_interview_date'] = post_data.get('end_interview_date')
            data['description'] = post_data.get('description')
            data['external_application_form'] = post_data.get('external_application_form')
            data['course'] = self.course.id

            form_kwargs['data'] = data
        return form_kwargs

    def form_valid(self, form):
        self.call_service(service=create_application_info, service_kwargs=form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy('dashboard:education:user-course-detail',
                                   kwargs={'course_id': self.course.id})

        return success_url
