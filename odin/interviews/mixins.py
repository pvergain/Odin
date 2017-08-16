from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from .models import Interview


class CheckInterviewDataMixin:
    def interview_data_validation(self):
        self.application_id = self.kwargs.get('application')

        if self.interview is None or \
           self.interview.application is None or \
           self.interview.application.user != self.request.user or \
           self.interview.application.id != int(self.application_id):
            raise Http404


class HasConfirmedInterviewRedirectMixin:
    def dispatch(self, request, *args, **kwargs):
        has_confirmed_interview_for_course = Interview.objects.filter(application=self.application, has_confirmed=True)
        if has_confirmed_interview_for_course.exists():
            interview = has_confirmed_interview_for_course.first()
            return redirect(reverse('dashboard:interviews:confirm-interview',
                            kwargs={'application_id': self.kwargs.get('application_id'),
                                    'interview_token': interview.uuid}))

        return super().dispatch(request, *args, **kwargs)
