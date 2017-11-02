from django.shortcuts import redirect
from django.views.generic import View, ListView, FormView, UpdateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404

from odin.users.models import BaseUser
from odin.users.services import create_user

from odin.interviews.services import add_course_to_interviewer_courses
from odin.interviews.models import Interviewer
from odin.education.models import Student, Teacher, Course, CourseAssignment
from odin.education.services import create_course, add_student, add_teacher

from odin.competitions.models import CompetitionJudge, CompetitionParticipant, Competition

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


class DashboardManagementView(DashboardManagementPermission,
                              ListView):
    template_name = 'dashboard/management.html'
    paginate_by = 101
    filter_class = UserFilter
    queryset = BaseUser.objects.select_related('profile').all()\
        .prefetch_related('student', 'teacher', 'interviewer',
                          'competitionjudge', 'competitionparticipant').order_by('-id')

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


class PromoteUserToJudgeView(DashboardManagementPermission,
                             View):
    def get(self, request, *args, **kwargs):
        instance = BaseUser.objects.get(id=kwargs.get('id'))
        CompetitionJudge.objects.create_from_user(instance)

        return redirect('dashboard:management:index')


class PromoteUserToParticipantView(DashboardManagementPermission,
                                   View):
    def get(self, request, *args, **kwargs):
        instance = BaseUser.objects.get(id=kwargs.get('id'))
        CompetitionParticipant.objects.create_from_user(instance)

        return redirect('dashboard:management:index')


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
