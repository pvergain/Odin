from django.shortcuts import redirect
from django.views.generic import (
    View,
    ListView,
    FormView,
    UpdateView,
    TemplateView
)
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404

from odin.users.models import BaseUser
from odin.users.services import create_user

from odin.interviews.services import add_course_to_interviewer_courses
from odin.interviews.models import Interviewer

from odin.education.models import Student, Teacher, Course, CourseAssignment
from odin.education.services import create_course, add_student, add_teacher

from odin.competitions.models import Competition

from odin.applications.models import Application, ApplicationInfo
from odin.applications.services import (
    get_partially_completed_applications,
    get_last_solutions_for_application,
    add_interview_person_to_application,
    generate_last_solutions_per_participant,
    get_valid_solutions,
    validate_can_add_interviewer_to_application
)

from odin.common.mixins import ReadableFormErrorsMixin, CallServiceMixin

from .permissions import DashboardManagementPermission
from .filters import UserFilter
from .mixins import DashboardCreateUserMixin
from .forms import (
    AddStudentToCourseForm,
    AddTeacherToCourseForm,
    ManagementAddCourseForm,
    AddCourseToInterviewerCoursesForm,
    AddParticipantToCompetitionForm,
    AddJudgeToCompetitionForm,
    AddCompetitionToCourseForm,
)

from odin.applications.forms import ApplicationInterviewerUpdateForm

from django.core.exceptions import ValidationError
from django.contrib import messages


class DashboardManagementView(DashboardManagementPermission,
                              ListView):
    template_name = 'dashboard/management.html'
    paginate_by = 101
    filter_class = UserFilter
    queryset = BaseUser.objects.select_related('profile').all()\
        .prefetch_related('student', 'teacher', 'interviewer',
                          'judge_in_competitions', 'participant_in_competitions').order_by('-id')

    def get_queryset(self):
        self.filter = self.filter_class(self.request.GET, queryset=self.queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.prefetch_related('students', 'teachers')
        context['competitions'] = Competition.objects.prefetch_related('participants', 'judges')

        return context


class PromoteUserToStudentView(DashboardManagementPermission,
                               View):
    def get(self, request, *args, **kwargs):
        instance = BaseUser.objects.get(id=kwargs.get('id'))
        Student.objects.create_from_user(instance)

        return redirect('dashboard:management:index')


class PromoteUserToTeacherView(DashboardManagementPermission,
                               View):
    def get(self, request, *args, **kwargs):
        instance = BaseUser.objects.get(id=kwargs.get('id'))
        Teacher.objects.create_from_user(instance)

        return redirect('dashboard:management:index')


class PromoteUserToInterviewerView(DashboardManagementPermission,
                                   View):
    def get(self, request, *args, **kwargs):
        instance = BaseUser.objects.get(id=kwargs.get('id'))
        interviewer = Interviewer.objects.create_from_user(instance)

        return redirect(reverse('dashboard:management:add-interviewer-to-course-with-initial',
                                kwargs={'interviewer_email': interviewer.email}))


class CreateUserView(DashboardCreateUserMixin, FormView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'user'

        return context

    def form_valid(self, form):
        create_user(**form.cleaned_data)

        return super().form_valid(form)


class CreateStudentView(DashboardCreateUserMixin, FormView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'student'

        return context

    def form_valid(self, form):
        instance = create_user(**form.cleaned_data)
        Student.objects.create_from_user(instance)

        return super().form_valid(form)


class CreateTeacherView(DashboardCreateUserMixin, FormView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'teacher'

        return context

    def form_valid(self, form):
        instance = create_user(**form.cleaned_data)
        Teacher.objects.create_from_user(instance)

        return super().form_valid(form)


class CreateCourseView(DashboardManagementPermission,
                       CallServiceMixin,
                       ReadableFormErrorsMixin,
                       FormView):
    template_name = 'dashboard/add_course.html'
    form_class = ManagementAddCourseForm

    def get_service(self):
        return create_course

    def form_valid(self, form):
        course = self.call_service(service_kwargs=form.cleaned_data)
        self.course_id = course.id

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course_id})


class EditCourseView(DashboardManagementPermission,
                     ReadableFormErrorsMixin,
                     UpdateView):
    model = Course
    form_class = ManagementAddCourseForm
    template_name = 'dashboard/edit_course.html'
    pk_url_kwarg = 'course_id'

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.kwargs.get('course_id')})


class AddStudentToCourseView(DashboardManagementPermission,
                             CallServiceMixin,
                             ReadableFormErrorsMixin,
                             FormView):
    template_name = 'dashboard/add_student_to_course.html'
    form_class = AddStudentToCourseForm
    success_url = reverse_lazy('dashboard:management:index')

    def get_service(self):
        return add_student

    def form_valid(self, form):
        self.call_service(service_kwargs=form.cleaned_data)

        return super().form_valid(form)


class AddParticipantToCompetitionView(DashboardManagementPermission,
                                      ReadableFormErrorsMixin,
                                      FormView):
    template_name = 'dashboard/add_participant_to_competition.html'
    form_class = AddParticipantToCompetitionForm
    success_url = reverse_lazy('dashboard:management:index')

    def form_valid(self, form):
        competition = form.cleaned_data.get('competition')
        participant = form.cleaned_data.get('participant')
        competition.participants.add(participant)

        return super().form_valid(form)


class AddTeacherToCourseView(DashboardManagementPermission,
                             CallServiceMixin,
                             ReadableFormErrorsMixin,
                             FormView):
    template_name = 'dashboard/add_teacher_to_course.html'
    form_class = AddTeacherToCourseForm
    success_url = reverse_lazy('dashboard:management:index')

    def get_service(self):
        return add_teacher

    def form_valid(self, form):
        teacher = form.cleaned_data.get('teacher')
        if teacher.is_superuser:
            course = form.cleaned_data.get('course')
            assignment = get_object_or_404(CourseAssignment, teacher=teacher, course=course)
            assignment.hidden = False
            assignment.save()
        else:
            self.call_service(service_kwargs=form.cleaned_data)

        return super().form_valid(form)


class AddJudgeToCompetitionView(DashboardManagementPermission,
                                ReadableFormErrorsMixin,
                                FormView):
    template_name = 'dashboard/add_judge_to_competition.html'
    form_class = AddJudgeToCompetitionForm
    success_url = reverse_lazy('dashboard:management:index')

    def form_valid(self, form):
        judge = form.cleaned_data.get('judge')
        competition = form.cleaned_data.get('competition')

        competition.judges.add(judge)

        return super().form_valid(form)


class AddCourseToInterviewerCoursesView(DashboardManagementPermission,
                                        CallServiceMixin,
                                        ReadableFormErrorsMixin,
                                        FormView):
    template_name = 'dashboard/add_course_to_interviewer_courses.html'
    form_class = AddCourseToInterviewerCoursesForm
    success_url = reverse_lazy('dashboard:management:index')

    def get_initial(self):
        initial = super().get_initial()
        interviewer_email = self.kwargs.get('interviewer_email')
        if interviewer_email:
            initial['interviewer'] = get_object_or_404(Interviewer, email=interviewer_email)

        return initial

    def get_service(self):
        return add_course_to_interviewer_courses

    def form_valid(self, form):
        self.call_service(service_kwargs=form.cleaned_data)

        return super().form_valid(form)


class AddCompetitionToCourseView(DashboardManagementPermission,
                                 ReadableFormErrorsMixin,
                                 FormView):
    template_name = 'dashboard/add_competition_to_course.html'
    form_class = AddCompetitionToCourseForm
    success_url = reverse_lazy('dashboard:management:index')

    def form_valid(self, form):
        competition = form.cleaned_data.get('competition')
        course = form.cleaned_data.get('course')

        course.application_info.competition = competition
        course.application_info.save()

        return super().form_valid(form)


class ApplicationsView(DashboardManagementPermission,
                       TemplateView):
    template_name = 'management/applications_view.html'

    def dispatch(self, request, *args, **kwargs):
        self.application_info = get_object_or_404(
            ApplicationInfo,
            pk=self.kwargs['application_info_id']
        )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        valid_solutions = get_valid_solutions(application_info=self.application_info,
                                              solutions=generate_last_solutions_per_participant())

        context['applications'] = get_partially_completed_applications(valid_solutions=valid_solutions,
                                                                       application_info=self.application_info)

        '''
        adding just the list of people that can do interviews a.k.a superusers
        '''
        context['interviewers'] = [interviewer for interviewer in
                                   BaseUser.objects.filter(is_superuser=True).values('id', 'email')]

        return context


class ApplicationSolutionsView(DashboardManagementPermission,
                               TemplateView):
    template_name = 'management/application_solutions.html'

    def dispatch(self, request, *args, **kwargs):
        self.application = get_object_or_404(
            Application,
            pk=self.kwargs['application_id']
        )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.application
        context['solutions'] = get_last_solutions_for_application(
            application=self.application
        )

        return context


class ApplicationInterviewPersonView(DashboardManagementPermission,
                                     UpdateView):

    model = Application
    form_class = ApplicationInterviewerUpdateForm
    pk_url_kwarg = 'application_id'
    template_name = 'management/application_interview_person.html'

    def form_valid(self, form):
        try:
            validate_can_add_interviewer_to_application(application=form.instance)
        except ValidationError as err:
            messages.warning(request=self.request, message=err.message)
            return super().form_invalid(form)
        add_interview_person_to_application(application=form.instance, **form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:management:applications',
                            kwargs={'application_info_id': self.request.POST['management_id']})
