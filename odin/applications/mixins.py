from django.shortcuts import redirect, reverse, get_object_or_404
from django.http import HttpResponseForbidden

from .models import ApplicationInfo


class ApplicationInfoFormDataMixin:
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


class ApplicationFormDataMixin:
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


class RedirectToExternalFormMixin:
    def dispatch(self, request, *args, **kwargs):
        application_info = get_object_or_404(ApplicationInfo, course=self.course)
        external_url = application_info.external_application_form
        if external_url:
            return redirect(external_url)
        return super().dispatch(request, *args, **kwargs)


class HasStudentAlreadyAppliedMixin:
    def dispatch(self, request, *args, **kwargs):
        self.user_applied = False
        if hasattr(request.user, 'applications') and hasattr(self.course, 'application_info'):
            user_application = request.user.applications.filter(application_info=self.course.application_info)
            if user_application.exists():
                self.user_applied = True
                url = reverse('dashboard:applications:edit-application', kwargs={'course_id': self.course.id})
                return redirect(url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_applied'] = self.user_applied
        return context


class ApplicationTasksMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().application_info.external_application_form:
            return HttpResponseForbidden("Can not edit an application with an external form")
        self.application_tasks = self.get_object().application_info.tasks.all()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_names = [task.name for task in self.application_tasks]
        context['task_names'] = task_names
        return context
