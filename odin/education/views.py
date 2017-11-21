import json
import calendar

from rest_framework import generics

from django.utils import timezone
from django.core.management import call_command
from django.conf import settings
from django.views import View
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    FormView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse, Http404

from odin.common.utils import transfer_POST_data_to_dict
from odin.common.mixins import CallServiceMixin, ReadableFormErrorsMixin
from odin.common.services import send_email
from odin.management.permissions import DashboardManagementPermission
from odin.grading.services import start_grader_communication

from .filters import SolutionsFilter
from .models import (
    Course,
    Teacher,
    Student,
    Material,
    Task,
    IncludedTask,
    Solution,
    IncludedTest,
    IncludedMaterial,
    CourseAssignment,
    Topic,
    Lecture,
    Certificate,
)
from .permissions import (
    IsStudentOrTeacherInCoursePermission,
    IsTeacherInCoursePermission,
    IsStudentInCoursePermission,
    IsStudentOrTeacherInCourseAPIPermission,
    CannotSubmitSolutionAfterCourseEndDate
)
from .mixins import (
    CourseViewMixin,
    PublicViewContextMixin,
    SubmitSolutionMixin,
    TaskViewMixin,
    HasTestMixin,
)
from .forms import (
    TopicModelForm,
    IncludedMaterialModelForm,
    IncludedMaterialFromExistingForm,
    IncludedTaskModelForm,
    IncludedTaskFromExistingForm,
    SourceCodeTestForm,
    BinaryFileTestForm,
    SubmitGradableSolutionForm,
    SubmitNonGradableSolutionForm,
    StudentNoteForm,
    CreateLectureForm,
    EditLectureForm,
    PlainTextForm,
    SolutionCommentForm,
)
from .services import (
    create_topic,
    create_included_material,
    create_included_task,
    create_test_for_task,
    create_gradable_solution,
    create_non_gradable_solution,
    calculate_student_valid_solutions_for_course,
    get_all_student_solution_statistics,
    create_student_note,
    create_solution_comment,
    create_lecture,
    add_week_to_course,
    get_certificate_data,
)
from .serializers import TopicSerializer, SolutionSerializer
from .utils import (
    get_solution_data,
    map_lecture_dates_to_week_days,
    get_all_solved_student_solution_count_for_course,
)


class UserCoursesView(LoginRequiredMixin, TemplateView):
    template_name = 'education/courses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        prefetch = ['students', 'teachers', 'weeks']
        qs = Course.objects.prefetch_related(*prefetch)

        context['user_is_teacher_for'] = []
        context['user_is_student_for'] = []

        teacher = user.downcast(Teacher)
        student = user.downcast(Student)

        if teacher:
            context['user_is_teacher_for'] = qs.filter(teachers=teacher)

        if student:
            context['user_is_student_for'] = qs.filter(students=student)

        return context


class CourseDetailView(LoginRequiredMixin,
                       CourseViewMixin,
                       IsStudentOrTeacherInCoursePermission,
                       TemplateView):

    template_name = 'education/course_detail_container.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_queryset = self.course.topics.prefetch_related(
            'tasks__solutions', 'materials', 'week', 'tasks__test__language'
        )
        topics = TopicSerializer(topic_queryset, many=True)
        course_topics = {}
        course_topics['data'] = topics.data
        context['course_topics'] = json.dumps(course_topics)
        if self.request.user.is_student():
            student = self.request.user.student
            context['tasks_ratio'] = calculate_student_valid_solutions_for_course(student=student, course=self.course)

        weekdays_with_lectures, course_schedule = map_lecture_dates_to_week_days(self.course)
        if course_schedule:
            context['course_schedule'] = course_schedule
            context['weekdays'] = weekdays_with_lectures
            context['humanized_weekdays'] = [calendar.day_name[i] for i in weekdays_with_lectures]

        context['is_user_teacher_in_course'] = self.is_teacher

        return context


class PublicCourseListView(PublicViewContextMixin, ListView):

    template_name = 'education/all_courses.html'

    def get_queryset(self):
        return Course.objects.filter(public=True).select_related('description').prefetch_related('weeks')


class PublicCourseDetailView(CourseViewMixin, PublicViewContextMixin, DetailView):
    def get_object(self):

        course_url = self.kwargs.get('course_slug')

        return get_object_or_404(Course, slug_url=course_url)


class AddTopicToCourseView(LoginRequiredMixin,
                           CourseViewMixin,
                           CallServiceMixin,
                           ReadableFormErrorsMixin,
                           IsTeacherInCoursePermission,
                           FormView):
    template_name = 'education/add_topic.html'
    form_class = TopicModelForm

    def get_service(self):
        return create_topic

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course

        return form_kwargs

    def form_valid(self, form):
        create_topic_kwargs = {
            'name': form.cleaned_data.get('name'),
            'week': form.cleaned_data.get('week'),
            'course': self.course
        }

        self.call_service(service_kwargs=create_topic_kwargs)

        return super().form_valid(form)


class EditTopicView(LoginRequiredMixin,
                    CourseViewMixin,
                    ReadableFormErrorsMixin,
                    IsTeacherInCoursePermission,
                    UpdateView):

    template_name = 'education/edit_topic.html'
    model = Topic
    pk_url_kwarg = 'topic_id'
    fields = ('name', 'week')

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})


class AddIncludedMaterialFromExistingView(LoginRequiredMixin,
                                          CourseViewMixin,
                                          CallServiceMixin,
                                          ReadableFormErrorsMixin,
                                          IsTeacherInCoursePermission,
                                          FormView):
    template_name = 'education/existing_material_list.html'
    form_class = IncludedMaterialFromExistingForm

    def get_service(self):
        return create_included_material

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['topic_id'] = self.kwargs.get('topic_id')

        context['material_list'] = Material.objects.prefetch_related('included_materials__topic__course')

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['topic'] = self.kwargs.get('topic_id')
            form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        data = {}
        data['existing_material'] = form.cleaned_data.get('material')
        data['topic'] = form.cleaned_data.get('topic')

        self.call_service(service_kwargs=data)

        return super().form_valid(form)


class ExistingMaterialListView(LoginRequiredMixin,
                               CourseViewMixin,
                               IsTeacherInCoursePermission,
                               ListView):
    template_name = 'education/existing_material_list.html'
    queryset = Material.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['topic_id'] = self.kwargs.get('topic_id')

        return context


class AddNewIncludedMaterialView(LoginRequiredMixin,
                                 CourseViewMixin,
                                 CallServiceMixin,
                                 ReadableFormErrorsMixin,
                                 IsTeacherInCoursePermission,
                                 FormView):
    template_name = 'education/add_material.html'
    form_class = IncludedMaterialModelForm

    def get_service(self):
        return create_included_material

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_initial(self):
        self.initial = super().get_initial()
        self.initial['topic'] = self.kwargs.get('topic_id')

        return self.initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course

        return form_kwargs

    def form_valid(self, form):
        create_included_material_kwargs = {
            'identifier': form.cleaned_data.get('identifier'),
            'url': form.cleaned_data.get('url'),
            'topic': form.cleaned_data.get('topic'),
            'content': form.cleaned_data.get('content')
        }

        self.call_service(service_kwargs=create_included_material_kwargs)

        return super().form_valid(form)


class EditIncludedMaterialView(LoginRequiredMixin,
                               CourseViewMixin,
                               ReadableFormErrorsMixin,
                               IsTeacherInCoursePermission,
                               UpdateView):

    model = IncludedMaterial
    form_class = IncludedMaterialModelForm
    pk_url_kwarg = 'material_id'
    template_name = 'education/edit_included_material.html'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course

        return form_kwargs

    def get_initial(self):
        instance = self.get_object()
        self.initial = super().get_initial()
        self.initial['topic'] = instance.topic.id

        return self.initial

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})


class ExistingTasksView(LoginRequiredMixin,
                        CourseViewMixin,
                        IsTeacherInCoursePermission,
                        FormView):
    template_name = 'education/existing_task_list.html'
    form_class = IncludedTaskFromExistingForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course

        data = transfer_POST_data_to_dict(self.request.POST)
        data['topic'] = self.kwargs.get('topic_id')
        form_kwargs['data'] = data

        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_list'] = Task.objects.all()
        context['topic_id'] = self.kwargs.get('topic_id')

        return context


class AddNewIncludedTaskView(LoginRequiredMixin,
                             CourseViewMixin,
                             CallServiceMixin,
                             ReadableFormErrorsMixin,
                             IsTeacherInCoursePermission,
                             FormView):
    template_name = 'education/add_task.html'
    form_class = IncludedTaskModelForm

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_initial(self):
        self.initial = super().get_initial()
        self.initial['topic'] = self.kwargs.get('topic_id')

        return self.initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course

        return form_kwargs

    def form_valid(self, form):
        create_included_task_kwargs = {
            'name': form.cleaned_data.get('name'),
            'description': form.cleaned_data.get('description'),
            'gradable': form.cleaned_data.get('gradable'),
            'topic': form.cleaned_data.get('topic')
        }

        task = self.call_service(service=create_included_task, service_kwargs=create_included_task_kwargs)
        if task.gradable:
            create_test_kwargs = {
                'task': task,
                'language': form.cleaned_data.get('language'),
                'code': form.cleaned_data.get('code') if form.cleaned_data.get('code') != '' else None,
                'file': form.cleaned_data.get('file')
            }

            self.call_service(service=create_test_for_task, service_kwargs=create_test_kwargs)

        return super().form_valid(form)


class AddIncludedTaskFromExistingView(LoginRequiredMixin,
                                      CourseViewMixin,
                                      CallServiceMixin,
                                      ReadableFormErrorsMixin,
                                      IsTeacherInCoursePermission,
                                      FormView):
    template_name = 'education/existing_task_list.html'
    form_class = IncludedTaskFromExistingForm

    def get_service(self):
        return create_included_task

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['topic_id'] = self.kwargs.get('topic_id')
        context['task_list'] = Task.objects.prefetch_related('included_tasks__topic__course')

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['topic'] = self.kwargs.get('topic_id')
            form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        create_included_task_kwargs = {
            'existing_task': form.cleaned_data.get('task'),
            'topic': form.cleaned_data.get('topic')
        }

        self.call_service(service_kwargs=create_included_task_kwargs)

        return super().form_valid(form)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    pk_url_kwarg = 'task_id'
    template_name = 'education/task_detail.html'


class IncludedTaskDetailView(LoginRequiredMixin,
                             CourseViewMixin,
                             TaskViewMixin,
                             IsStudentOrTeacherInCoursePermission,
                             DetailView):
    model = IncludedTask
    pk_url_kwarg = 'task_id'
    template_name = 'education/task_detail.html'


class MaterialDetailView(LoginRequiredMixin,
                         DetailView):
    model = Material
    pk_url_kwarg = 'material_id'
    template_name = 'education/material_detail'


class IncludedMaterialDetailView(LoginRequiredMixin,
                                 CourseViewMixin,
                                 IsStudentOrTeacherInCoursePermission,
                                 DetailView):
    model = IncludedMaterial
    pk_url_kwarg = 'material_id'
    template_name = 'education/material_detail.html'


class EditTaskView(LoginRequiredMixin,
                   ReadableFormErrorsMixin,
                   DashboardManagementPermission,
                   UpdateView):

    model = Task
    fields = ('name', 'description', 'gradable')
    pk_url_kwarg = 'task_id'
    template_name = 'education/edit_task.html'

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-courses')


class EditIncludedTaskView(LoginRequiredMixin,
                           CourseViewMixin,
                           ReadableFormErrorsMixin,
                           IsTeacherInCoursePermission,
                           UpdateView):

    model = IncludedTask
    form_class = IncludedTaskModelForm
    pk_url_kwarg = 'task_id'
    template_name = 'education/edit_included_task.html'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course

        return form_kwargs

    def get_initial(self):
        instance = self.get_object()
        self.initial = super().get_initial()
        self.initial['topic'] = instance.topic.id

        return self.initial

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})


class AddSourceCodeTestToTaskView(LoginRequiredMixin,
                                  CourseViewMixin,
                                  CallServiceMixin,
                                  ReadableFormErrorsMixin,
                                  IsTeacherInCoursePermission,
                                  FormView):

    form_class = SourceCodeTestForm
    template_name = 'education/add_source_test.html'

    def get_service(self):
        return create_test_for_task

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['task'] = self.kwargs.get('task_id')

            form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        self.call_service(service_kwargs=form.cleaned_data)

        return super().form_valid(form)


class AddBinaryFileTestToTaskView(LoginRequiredMixin,
                                  CourseViewMixin,
                                  CallServiceMixin,
                                  ReadableFormErrorsMixin,
                                  IsTeacherInCoursePermission,
                                  FormView):

    form_class = BinaryFileTestForm
    template_name = 'education/add_binary_test.html'

    def get_service(self):
        return create_test_for_task

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['task'] = self.kwargs.get('task_id')

            form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        self.call_service(service_kwargs=form.cleaned_data)

        return super().form_valid(form)


class EditIncludedTestView(LoginRequiredMixin,
                           CourseViewMixin,
                           ReadableFormErrorsMixin,
                           IsTeacherInCoursePermission,
                           UpdateView):
    model = IncludedTest
    template_name = 'education/edit_included_test.html'

    def get_object(self):
        task = IncludedTask.objects.get(id=self.kwargs.get('task_id'))

        return task.test

    def get_form_class(self):
        if self.object.is_source():
            return SourceCodeTestForm

        return BinaryFileTestForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['task'] = self.kwargs.get('task_id')

            form_kwargs['data'] = data

        return form_kwargs

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})


class StudentSolutionListView(LoginRequiredMixin,
                              CourseViewMixin,
                              TaskViewMixin,
                              IsStudentInCoursePermission,
                              ListView):
    template_name = 'education/student_solution_list.html'

    def get_queryset(self):
        user = self.request.user
        task = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))

        return Solution.objects.get_solutions_for(user.student, task)


class StudentSolutionDetailView(LoginRequiredMixin,
                                CourseViewMixin,
                                IsStudentOrTeacherInCoursePermission,
                                DetailView):
    model = Solution
    pk_url_kwarg = 'solution_id'
    template_name = 'education/student_solution_detail.html'

    def get_object(self):
        solution = Solution.objects.filter(id=self.kwargs.get('solution_id'))\
               .prefetch_related('comments__user').first()
        if solution:
            return solution
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solution = self.object
        context['role'] = solution.student
        context['solution'] = solution
        if solution.task.gradable and not solution.task.test.is_source():
            try:
                context['solution_file'] = solution.file.read().decode('utf-8')
            except UnicodeDecodeError as e:
                context['solution_file'] = "Invalid file format"

        return context


class SubmitGradableSolutionView(LoginRequiredMixin,
                                 CourseViewMixin,
                                 TaskViewMixin,
                                 CallServiceMixin,
                                 ReadableFormErrorsMixin,
                                 SubmitSolutionMixin,
                                 HasTestMixin,
                                 IsStudentInCoursePermission,
                                 CannotSubmitSolutionAfterCourseEndDate,
                                 FormView):
    form_class = SubmitGradableSolutionForm

    def get_service(self):
        return create_gradable_solution

    def get(self, request, *args, **kwargs):
        res = self.has_test()

        return res or super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        res = self.has_test()

        return res or super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        task = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        test = task.test

        form_kwargs['is_test_source'] = test.is_source()

        return form_kwargs

    def form_valid(self, form):
        create_gradable_solution_kwargs = {
            'student': self.request.user.student,
            'task': get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        }
        create_gradable_solution_kwargs.update(form.cleaned_data)

        solution = self.call_service(service_kwargs=create_gradable_solution_kwargs)
        if solution:
            self.solution_id = solution.id
            start_grader_communication(solution.id, 'education.Solution')

        return super().form_valid(form)

    def form_invalid(self, form):
        if not self.request.is_ajax():
            return super().form_invalid(form)
        else:
            data = {
                'errors': form.errors
            }
            return JsonResponse(data=data)


class SubmitNonGradableSolutionView(LoginRequiredMixin,
                                    CourseViewMixin,
                                    TaskViewMixin,
                                    CallServiceMixin,
                                    ReadableFormErrorsMixin,
                                    SubmitSolutionMixin,
                                    IsStudentInCoursePermission,
                                    CannotSubmitSolutionAfterCourseEndDate,
                                    FormView):
    form_class = SubmitNonGradableSolutionForm

    def get_service(self):
        return create_non_gradable_solution

    def form_valid(self, form):
        create_non_gradable_solution_kwargs = {
            'student': self.request.user.student,
            'task': get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        }
        create_non_gradable_solution_kwargs.update(form.cleaned_data)

        solution = self.call_service(service_kwargs=create_non_gradable_solution_kwargs)
        if solution:
            self.solution_id = solution.id

        return super().form_valid(form)

    def form_invalid(self, form):
        if not self.request.is_ajax():
            return super().form_invalid(form)
        else:
            data = {
                'errors': form.errors
            }
            return JsonResponse(data=data)


class CourseStudentsListView(LoginRequiredMixin,
                             CourseViewMixin,
                             IsTeacherInCoursePermission,
                             ListView):
    template_name = 'education/course_students.html'

    def get_queryset(self):
        prefetch = ('notes__author', 'student__solutions__task')
        qs = CourseAssignment.objects.filter(course=self.course).exclude(teacher__isnull=False)
        return qs.select_related('student__profile').prefetch_related(*prefetch)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_count'] = IncludedTask.objects.filter(topic__course=self.course).count()
        context['students_passed_solutions'] = get_all_solved_student_solution_count_for_course(course=self.course)

        return context


class AllStudentsSolutionsView(LoginRequiredMixin,
                               CourseViewMixin,
                               TaskViewMixin,
                               IsTeacherInCoursePermission,
                               ListView):
    template_name = "education/all_students_solutions.html"
    filter_class = SolutionsFilter

    def get_queryset(self):
        task = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        queryset = self.course.students.select_related('profile').prefetch_related('solutions__task').distinct().all()
        self.filter = self.filter_class(self.request.GET, queryset=queryset, task=task)

        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        context['solution_statistics'] = get_all_student_solution_statistics(task=task)

        return context


class SolutionDetailAPIView(generics.RetrieveAPIView):
    serializer_class = SolutionSerializer
    permission_classes = (IsStudentOrTeacherInCourseAPIPermission, )
    queryset = Solution.objects.all()
    lookup_url_kwarg = 'solution_id'


class CompareSolutionsView(LoginRequiredMixin,
                           CourseViewMixin,
                           IsTeacherInCoursePermission,
                           TemplateView):
    template_name = 'education/solution_comparison.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comparison_result'] = call_command('compare_solutions', self.course.id)

        return context


class CourseStudentDetailView(LoginRequiredMixin,
                              CourseViewMixin,
                              IsTeacherInCoursePermission,
                              DetailView):
    template_name = 'education/course_student_detail.html'
    model = Student
    slug_url_kwarg = 'email'
    slug_field = 'email'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        student = self.object
        course_topics = self.course.topics.all()
        tasks_with_solution = []
        for topic in course_topics:
            tasks_with_solution += topic.tasks.all()
        course_tasks = tasks_with_solution
        context['course_tasks'] = course_tasks
        task_solutions = {}
        solution_data, passed_or_failed = get_solution_data(self.course, student)
        for task in course_tasks:
            if not passed_or_failed.get(task.name):
                passed_or_failed[task.name] = "Not submitted"
            task_solutions[task] = (solution_data.get(task), passed_or_failed.get(task.name))

        context['task_solutions'] = task_solutions
        assignment = get_object_or_404(CourseAssignment, student=student, course=self.course)
        context['assignment'] = assignment
        context['students_passed_solutions'] = get_all_solved_student_solution_count_for_course(course=self.course)

        return context


class CreateStudentNoteView(LoginRequiredMixin,
                            CourseViewMixin,
                            ReadableFormErrorsMixin,
                            IsTeacherInCoursePermission,
                            CallServiceMixin,
                            FormView):
    form_class = StudentNoteForm
    template_name = 'education/partial/notes_section.html'

    def get_success_url(self):
        if self.request.POST.get('detail') != 'true':
            url = reverse_lazy('dashboard:education:course-students-list',
                               kwargs={
                                   'course_id': self.course.id
                               })
            if hasattr(self, 'student'):
                return url + f'#notes-section_{self.student.id}'
        else:
            url = reverse_lazy('dashboard:education:course-student-detail',
                               kwargs={
                                   'course_id': self.course.id,
                                   'email': self.student.email
                               }) + f'#notes-section_{self.student.id}'

        return url

    def get(self, request, *args, **kwargs):
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        self.student = get_object_or_404(Student, pk=form.data.get('student'))

        for field, error in form.errors.items():
            messages.warning(request=self.request, message=f'Empty note!')

        return redirect(self.get_success_url())

    def get_service(self):
        return create_student_note

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['author'] = self.request.user.teacher
            data['assignment'] = get_object_or_404(CourseAssignment, course=self.course, student=data['student']).id

            form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        service_kwargs = form.cleaned_data
        self.student = service_kwargs.pop('student')
        self.call_service(service_kwargs=service_kwargs)

        return super().form_valid(form)


class CreateSolutionCommentView(LoginRequiredMixin,
                                CourseViewMixin,
                                IsStudentOrTeacherInCoursePermission,
                                CallServiceMixin,
                                FormView):
    form_class = SolutionCommentForm
    template_name = 'education/partial/comments_section.html'
    http_method_names = [u'post', u'put']

    def get_success_url(self):
        solution = self.solution
        return reverse_lazy('dashboard:education:student-solution-detail',
                            kwargs={
                                'course_id': self.course.id,
                                'task_id': solution.task.id,
                                'solution_id': solution.id
                            }) + f"#comments-section_{solution.id}"

    def get_service(self):
        return create_solution_comment

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        data = transfer_POST_data_to_dict(self.request.POST)
        data['user'] = self.request.user.id
        self.solution = get_object_or_404(Solution, id=data.get('solution'))
        if data.get('student') != str(self.solution.student.id):
            raise Http404("Not this student's solution!")

        form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        service_kwargs = form.cleaned_data
        self.call_service(service_kwargs=service_kwargs)

        return super().form_valid(form)

    def form_invalid(self, form):
        for field, error in form.errors.items():
            messages.warning(request=self.request, message=f'Empty comment!')

        return redirect(self.get_success_url())


class CreateLectureView(LoginRequiredMixin,
                        CourseViewMixin,
                        IsTeacherInCoursePermission,
                        CallServiceMixin,
                        ReadableFormErrorsMixin,
                        FormView):
    template_name = 'education/create_lecture.html'
    form_class = CreateLectureForm

    def get_service(self):
        return create_lecture

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={
                                'course_id': self.course.id
                            })

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['course'] = self.course.id
            form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        lecture = self.call_service(service_kwargs=form.cleaned_data)

        if not lecture:
            return super().form_invalid(form)

        return super().form_valid(form)


class EditLectureView(LoginRequiredMixin,
                      CourseViewMixin,
                      IsTeacherInCoursePermission,
                      ReadableFormErrorsMixin,
                      UpdateView):
    template_name = 'education/edit_lecture.html'
    form_class = EditLectureForm

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={
                                'course_id': self.course.id
                            })

    def get_object(self):
        return get_object_or_404(Lecture, id=self.kwargs.get('lecture_id'), course=self.course)


class DeleteLectureView(LoginRequiredMixin,
                        CourseViewMixin,
                        IsTeacherInCoursePermission,
                        DeleteView):
    model = Lecture
    pk_url_kwarg = 'lecture_id'
    http_method_names = ['post', 'put', 'delete']

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={
                                'course_id': self.course.id
                            })


class AddWeekToCourseView(LoginRequiredMixin,
                          CourseViewMixin,
                          IsTeacherInCoursePermission,
                          View):

    http_method_names = ['post', 'put']
    template_name = 'education/teacher_course_detail.html'

    def post(self, request, *args, **kwargs):
        add_week_to_course(course=self.course, new_end_date=self.course.end_date + timezone.timedelta(days=7))

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail', kwargs={
           'course_id': self.course.id
        })


class SendEmailToAllStudentsView(LoginRequiredMixin,
                                 CourseViewMixin,
                                 IsTeacherInCoursePermission,
                                 FormView):
    form_class = PlainTextForm
    template_name = 'education/send_email_to_all_students.html'

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={
                                'course_id': self.course.id
                            })

    def form_valid(self, form):
        template_name = settings.EMAIL_TEMPLATES.get('course_information_email')
        context = {
            'course': self.course.name,
            'information': form.cleaned_data.get('text')
        }

        recipients = [student.email for student in self.course.students.all()]
        send_email(template_name=template_name, recipients=recipients, context=context)

        return super().form_valid(form)


class CertificateDetailView(DetailView):
    def get_object(self):
        return get_object_or_404(Certificate, token=self.kwargs.get('certificate_token'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        course_data = get_certificate_data(assignment=self.object.assignment)

        context['gradable_tasks'] = course_data["gradable_tasks"]
        context['non_gradable_tasks'] = course_data["non_gradable_tasks"]
        context['percent_awesome'] = course_data["percent_awesome"]

        return context
