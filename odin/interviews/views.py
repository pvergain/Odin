from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse
from django.shortcuts import redirect

from odin.applications.models import Application
from odin.common.mixins import CallServiceMixin, ReadableFormErrorsMixin

from .permissions import CannotConfirmOthersInterviewPermission
from .mixins import CheckInterviewDataMixin
from .models import Interview
from .services import create_new_interview_for_application
from .forms import ChooseInterviewForm


class ChooseInterviewView(LoginRequiredMixin,
                          CannotConfirmOthersInterviewPermission,
                          CallServiceMixin,
                          ReadableFormErrorsMixin,
                          CheckInterviewDataMixin,
                          FormView):
    form_class = ChooseInterviewForm
    template_name = 'interviews/choose_interview.html'

    def get_service(self):
        return create_new_interview_for_application

    def get(self, request, *args, **kwargs):
        if self.interview.has_confirmed:
            return redirect(reverse('dashboard:interviews:confirm_interview',
                            kwargs={'application_id': self.kwargs.application_id,
                                    'interview_token': self.interview.uuid}))

        return super().get(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        uuid = self.kwargs.get('interview_token')
        application_id = self.kwargs.get('application_id')
        context['current_interview'] = Interview.objects.filter(uuid=uuid).first()
        application = Application.objects.filter(id=application_id).first()
        context['application'] = application
        context['interviews'] = Interview.objects.free_slots_for(application.application_info)

        return context

    def form_valid(self, form):
        interview = Interview.objects.filter(id=form.cleaned_data.get('interviews')).first()
        uuid = interview.uuid
        application = Application.objects.filter(id=self.kwargs.get('application_id')).first()
        service_kwargs = {
            'uuid': uuid,
            'application': application,
        }
        self.call_service(service_kwargs=service_kwargs)
        return super().form_valid(form)
