from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, View, ListView, DeleteView, UpdateView, TemplateView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect

from odin.management.permissions import DashboardManagementPermission
from odin.applications.models import Application, ApplicationInfo
from odin.common.mixins import CallServiceMixin, ReadableFormErrorsMixin
from odin.common.permissions import IsSuperuserPermission
from odin.common.utils import transfer_POST_data_to_dict

from rest_framework import generics

from .permissions import (
    CannotConfirmOthersInterviewPermission,
    IsInterviewerPermission,
    CannotControlOtherInterviewerDataPermission
)
from .mixins import CheckInterviewDataMixin, HasConfirmedInterviewRedirectMixin, UserInterviewsListMixin
from .models import Interview, InterviewerFreeTime
from .services import create_new_interview_for_application, create_interviewer_free_time, generate_interview_slots
from .forms import FreeTimeModelForm
from .tasks import send_interview_confirmation_emails, assign_accepted_users_to_courses
from .serializers import InterviewSerializer


class ChooseInterviewView(LoginRequiredMixin,
                          CannotConfirmOthersInterviewPermission,
                          HasConfirmedInterviewRedirectMixin,
                          CallServiceMixin,
                          CheckInterviewDataMixin,
                          TemplateView):
    template_name = 'interviews/choose_interview.html'

    def get_service(self):
        return create_new_interview_for_application

    def post(self, request, *args, **kwargs):
        uuid = kwargs.get('interview_token')
        application = self.application

        service_kwargs = {
            'uuid': uuid,
            'application': application,
        }
        interview = self.call_service(service_kwargs=service_kwargs)

        return redirect(reverse('dashboard:interviews:confirm-interview',
                                kwargs={'application_id': interview.application.id,
                                        'interview_token': str(interview.uuid)}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        uuid = self.kwargs.get('interview_token')
        application_id = self.kwargs.get('application_id')
        context['current_interview'] = Interview.objects.filter(uuid=uuid).first()
        application = Application.objects.filter(id=application_id).first()
        context['application'] = application
        context['interviews'] = Interview.objects.free_slots_for(application.application_info)

        return context


class InterviewsListView(LoginRequiredMixin,
                         IsSuperuserPermission,
                         IsInterviewerPermission,
                         UserInterviewsListMixin,
                         ListView):
    template_name = 'interviews/interviews_list.html'


class GenerateInterviewsView(DashboardManagementPermission, UserInterviewsListMixin, TemplateView):
    http_method_names = ['post', 'put']
    template_name = 'interviews/interviews_list.html'

    def post(self, request, *args, **kwargs):
        context = generate_interview_slots()
        kwargs['log'] = context['log']

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['log'] = kwargs['log']
        context['object_list'] = self.get_queryset()

        return context


class CreateFreeTimeView(LoginRequiredMixin,
                         IsInterviewerPermission,
                         ReadableFormErrorsMixin,
                         CallServiceMixin,
                         FormView):
    form_class = FreeTimeModelForm
    template_name = 'interviews/create_free_time.html'
    success_url = reverse_lazy('dashboard:interviews:user-interviews')

    def get_service(self):
        return create_interviewer_free_time

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['interviewer'] = self.request.user.interviewer
            form_kwargs['data'] = data
        return form_kwargs

    def form_valid(self, form):
        self.call_service(service=self.get_service(), service_kwargs=form.cleaned_data)

        return super().form_valid(form)


class DeleteFreeTimeView(LoginRequiredMixin,
                         CannotControlOtherInterviewerDataPermission,
                         DeleteView):
    model = InterviewerFreeTime
    pk_url_kwarg = 'free_time_id'
    success_url = reverse_lazy('dashboard:interviews:user-interviews')
    http_method_names = ['post', 'delete', 'put']


class UpdateFreeTimeView(LoginRequiredMixin,
                         CannotControlOtherInterviewerDataPermission,
                         ReadableFormErrorsMixin,
                         UpdateView):
    model = InterviewerFreeTime
    pk_url_kwarg = 'free_time_id'
    form_class = FreeTimeModelForm
    template_name = 'interviews/create_free_time.html'
    success_url = reverse_lazy('dashboard:interviews:user-interviews')

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['interviewer'] = self.request.user.interviewer
            form_kwargs['data'] = data

        return form_kwargs


class ConfirmInterviewView(LoginRequiredMixin,
                           CannotConfirmOthersInterviewPermission,
                           TemplateView):
    template_name = 'interviews/confirm_interview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['interview'] = self.interview
        context['application'] = self.application
        context['interviewer'] = self.interviewer

        return context

    def post(self, request, *args, **kwargs):
        has_confirmed_interview_for_course = Interview.objects.filter(application=self.application, has_confirmed=True)
        if not has_confirmed_interview_for_course.exists():
            self.interview.has_confirmed = True
            self.interview.save()

        return super().get(request, *args, **kwargs)


class FreeInterviewsListAPIView(generics.ListAPIView):
    serializer_class = InterviewSerializer
    queryset = Interview.objects.get_free_slots().order_by('date', 'start_time')

    def get_serializer_context(self):
        return {'application': self.request.GET.get('application_id')}


class SendInterviewConfirmationEmailsView(DashboardManagementPermission, View):
    def post(self, request, *args, **kwargs):
        send_interview_confirmation_emails.delay()

        return redirect('dashboard:interviews:user-interviews')


class RateInterviewView(LoginRequiredMixin,
                        CannotControlOtherInterviewerDataPermission,
                        ReadableFormErrorsMixin,
                        UpdateView):
    model = Interview
    fields = [
        'code_skills_rating',
        'code_design_rating',
        'fit_attitude_rating',
        'interviewer_comment',
        'is_accepted'
    ]
    slug_url_kwarg = 'interview_token'
    slug_field = 'uuid'
    template_name = "interviews/rate_interview.html"
    success_url = reverse_lazy('dashboard:interviews:user-interviews')

    def form_valid(self, form):
        application = self.get_object().application
        application.is_accepted = form.cleaned_data.get('is_accepted')
        application.save()

        return super().form_valid(form)


class AcceptedApplicantsListView(LoginRequiredMixin,
                                 IsSuperuserPermission,
                                 IsInterviewerPermission,
                                 ListView):
    template_name = 'interviews/accepted_applicants.html'

    def get_queryset(self):
        return ApplicationInfo.objects.get_open_for_interview()


class PromoteAcceptedUsersToStudentsView(LoginRequiredMixin,
                                         DashboardManagementPermission,
                                         View):
    def post(self, request, *args, **kwargs):
        assign_accepted_users_to_courses.delay()

        return redirect('dashboard:interviews:accepted-applicants')


class DeleteInterviewView(LoginRequiredMixin,
                          CannotControlOtherInterviewerDataPermission,
                          DeleteView):
    model = Interview
    slug_url_kwarg = 'interview_token'
    slug_field = 'uuid'
    success_url = reverse_lazy('dashboard:interviews:user-interviews')
    http_method_names = ['post', 'delete', 'put']
