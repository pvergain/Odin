from django.views.generic import (
    FormView,
    UpdateView,
    ListView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404

from odin.common.mixins import CallServiceMixin, ReadableFormErrorsMixin

from odin.education.mixins import CourseViewMixin
from odin.education.models import Course
from odin.education.permissions import IsTeacherInCoursePermission

from odin.competitions.models import Solution

from .permissions import ViewApplicationDetailPermission
from .models import Application, ApplicationInfo
from .forms import (
    ApplicationInfoModelForm,
    ApplicationCreateForm,
    ApplicationEditForm
)
from .services import (
    create_application_info,
    create_application
)
from .mixins import (
    ApplicationInfoFormDataMixin,
    HasStudentAlreadyAppliedMixin,
    ApplicationFormDataMixin,
    RedirectToExternalFormMixin
)


class CreateApplicationInfoView(LoginRequiredMixin,
                                CourseViewMixin,
                                IsTeacherInCoursePermission,
                                ApplicationInfoFormDataMixin,
                                CallServiceMixin,
                                ReadableFormErrorsMixin,
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


class EditApplicationInfoView(LoginRequiredMixin,
                              CourseViewMixin,
                              IsTeacherInCoursePermission,
                              ApplicationInfoFormDataMixin,
                              ReadableFormErrorsMixin,
                              UpdateView):

    form_class = ApplicationInfoModelForm
    template_name = "applications/create_application_info.html"

    def get_object(self):
        return self.course.application_info

    def get_success_url(self):
        success_url = reverse_lazy('dashboard:education:user-course-detail',
                                   kwargs={'course_id': self.course.id})

        return success_url


class ApplyToCourseView(LoginRequiredMixin,
                        CourseViewMixin,
                        RedirectToExternalFormMixin,
                        ApplicationFormDataMixin,
                        HasStudentAlreadyAppliedMixin,
                        CallServiceMixin,
                        ReadableFormErrorsMixin,
                        FormView):

    form_class = ApplicationCreateForm
    template_name = "applications/course_application.html"

    def get_service(self):
        return create_application

    def get_success_url(self):
        return reverse_lazy('dashboard:applications:user-applications')

    def form_valid(self, form):
        self.application = self.call_service(service_kwargs=form.cleaned_data)

        if self.course.application_info.has_competition:
            messages.success(
                self.request,
                'Your application is submitted but not ready. Check the "edit" application buttow below.'
            )
        else:
            messages.succes(
                self.request,
                'Your application is submited & ready.'
            )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['application_has_competition'] = self.course.application_info.has_competition

        return context


class UserApplicationsListView(LoginRequiredMixin,
                               ListView):
    template_name = 'applications/user_applications_list.html'

    def get_queryset(self):
        prefetch = [
            'application_info__course'
        ]

        return Application.objects.filter(user=self.request.user).prefetch_related(*prefetch)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_teacher():
            teacher = self.request.user.teacher
            prefetch = [
                'application_info__applications__user__profile'
            ]
            filters = {
                'teachers__in': [teacher]
            }

            courses = Course.objects.get_in_application_period().filter(**filters)
            context['teached_courses'] = courses.prefetch_related(*prefetch).order_by('-start_date')
        courses_open_for_application = [app_info.course for app_info in ApplicationInfo.objects.get_open_for_apply()]
        context['courses_open_for_application'] = courses_open_for_application

        return context


class EditApplicationView(LoginRequiredMixin,
                          CourseViewMixin,
                          ReadableFormErrorsMixin,
                          UpdateView):
    form_class = ApplicationEditForm
    template_name = 'applications/edit_application.html'

    success_url = reverse_lazy('dashboard:applications:user-applications')

    def get_object(self):
        return get_object_or_404(
            Application,
            user=self.request.user,
            application_info__course=self.course
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        application_info = self.object.application_info

        if application_info.has_competition:
            last_solutions = {}

            for competition_task in application_info.competition.tasks.all():
                last_solutions[competition_task.id] = Solution.objects.filter(
                    participant=self.request.user,
                    task=competition_task
                ).order_by('-id').first()

            context['last_solutions'] = last_solutions

        return context


class ApplicationDetailView(LoginRequiredMixin,
                            ViewApplicationDetailPermission,
                            DetailView):
    model = Application
    template_name = 'applications/application_detail.html'
    pk_url_kwarg = 'application_id'


class PublicCourseApplyView(DetailView):
    template_name = 'applications/public_apply.html'

    def get_object(self):
        course_url = self.kwargs.get('course_slug')

        return get_object_or_404(Course, slug_url=course_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['is_user_authenticated'] = self.request.user.is_authenticated

        next_action_url = reverse(
            'dashboard:applications:apply-to-course',
            kwargs={
                'course_slug': self.object.slug_url
            }
        )

        register_url = reverse('account_signup')
        login_url = reverse('account_login')
        course_apply_url = reverse(
            'dashboard:applications:apply-to-course',
            kwargs={
                'course_slug': self.object.slug_url
            }
        )

        context['register_url'] = f'{register_url}?next={next_action_url}'
        context['login_url'] = f'{login_url}?next={next_action_url}'
        context['course_apply_url'] = course_apply_url

        return context
