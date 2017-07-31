from django.views.generic import FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.conf import settings

from odin.common.services import send_email
from odin.education.mixins import CourseViewMixin, CallServiceMixin
from odin.education.permissions import IsTeacherInCoursePermission
from .forms import ApplicationInfoModelForm, IncludedApplicationTaskForm, ApplicationForm
from .services import create_application_info, create_included_application_task, create_application
from .mixins import ApplicationInfoFormDataMixin, HasStudentAlreadyAppliedMixin


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
                        HasStudentAlreadyAppliedMixin,
                        CallServiceMixin,
                        FormView):

    form_class = ApplicationForm
    template_name = "applications/course_application.html"

    def get_success_url(self):
        return reverse_lazy('public:course_detail',
                            kwargs={'course_slug': self.course.slug_url})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            post_data = self.request.POST
            data = {}
            data['application_info'] = self.course.application_info.id
            data['user'] = self.request.user.id
            data['phone'] = post_data.get('phone')
            data['skype'] = post_data.get('skype')
            data['works_at'] = post_data.get('works_at')
            data['studies_at'] = post_data.get('studies_at')

            form_kwargs['data'] = data

        return form_kwargs

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
