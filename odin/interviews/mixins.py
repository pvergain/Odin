from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from .models import Interview, Interviewer, InterviewerFreeTime


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


class UserInterviewsListMixin:
    def get_queryset(self):
        if self.request.user.is_interviewer():
            interviewer = get_object_or_404(Interviewer, user=self.request.user)
            related = 'application__user__profile'
            return Interview.objects.filter(interviewer=interviewer, application__isnull=False).select_related(related)
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_interviewer():
            interviewer = get_object_or_404(Interviewer, user=self.request.user)
            context['free_interview_dates'] = Interview.objects.filter(interviewer=interviewer, has_confirmed=False)
            context['free_time_slots'] = interviewer.free_time_slots.all()
        if self.request.user.is_superuser:
            context['all_free_time_slots'] = InterviewerFreeTime.objects.select_related('interviewer__user__profile')

        return context
