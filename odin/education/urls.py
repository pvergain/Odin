from django.conf.urls import url, include

from .views import (
    UserCoursesView,
    CourseDetailView,
    PublicCourseListView,
    PublicCourseDetailView,
    AddTopicToCourseView,
    AddNewIncludedMaterialView,
    AddIncludedMaterialFromExistingView,
    ExistingMaterialListView,
    AddNewIncludedTaskView,
    AddIncludedTaskFromExistingView,
    ExistingTasksView,
    TaskDetailView,
    EditTaskView,
    EditIncludedTaskView,
    AddBinaryFileTestToTaskView,
    AddSourceCodeTestToTaskView,
    StudentSolutionListView,
    SubmitGradableSolutionView,
    SubmitNonGradableSolutionView,
    StudentSolutionDetailView,
    EditIncludedTestView,
    MaterialDetailView,
    AllStudentsSolutionsView
)


courses_public_urlpatterns = [
    url(
        regex='^$',
        view=PublicCourseListView.as_view(),
        name='courses'
    ),
    url(
        regex='^(?P<course_slug>[-\w]+)/$',
        view=PublicCourseDetailView.as_view(),
        name='course_detail'
    ),
]

course_management_urlpatterns = [
    url(
        regex='^(?P<course_id>[0-9]+)/add-topic/$',
        view=AddTopicToCourseView.as_view(),
        name='manage-course-topics'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/(?P<topic_id>[0-9]+)/existing-materials/$',
        view=ExistingMaterialListView.as_view(),
        name='existing-materials'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/(?P<topic_id>[0-9]+)/add-material/existing$',
        view=AddIncludedMaterialFromExistingView.as_view(),
        name='add-included-material-from-existing'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/(?P<topic_id>[0-9]+)/add-material/new$',
        view=AddNewIncludedMaterialView.as_view(),
        name='add-new-included-material'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/(?P<topic_id>[0-9]+)/existing-tasks/$',
        view=ExistingTasksView.as_view(),
        name='existing-tasks'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/(?P<topic_id>[0-9]+)/add-task/existing$',
        view=AddIncludedTaskFromExistingView.as_view(),
        name='add-included-task-from-existing'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/add-task/new$',
        view=AddNewIncludedTaskView.as_view(),
        name='add-new-included-task'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/edit-included-task/(?P<task_id>[0-9]+)/$',
        view=EditIncludedTaskView.as_view(),
        name='edit-included-task'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/add-source-test/(?P<task_id>[0-9]+)$',
        view=AddSourceCodeTestToTaskView.as_view(),
        name='add-source-test'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/add-binary-test/(?P<task_id>[0-9]+)$',
        view=AddBinaryFileTestToTaskView.as_view(),
        name='add-binary-test'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/edit-test-for-task/(?P<task_id>[0-9]+)$',
        view=EditIncludedTestView.as_view(),
        name='edit-test'
    ),

]

urlpatterns = [
    url(
        regex='^my-courses/$',
        view=UserCoursesView.as_view(),
        name='user-courses'
    ),
    url(
        regex='^my-courses/(?P<course_id>[0-9]+)/$',
        view=CourseDetailView.as_view(),
        name='user-course-detail'
    ),
    url(
        regex='^manage-course/',
        view=include(course_management_urlpatterns,
                     namespace='course-management')
    ),
    url(
        regex='^tasks/edit-task/(?P<task_id>[0-9]+)/$',
        view=EditTaskView.as_view(),
        name='edit-task'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/tasks/(?P<task_id>[0-9]+)/solutions$',
        view=StudentSolutionListView.as_view(),
        name='user-task-solutions'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/tasks/(?P<task_id>[0-9]+)/add-gradable-solution$',
        view=SubmitGradableSolutionView.as_view(),
        name='add-gradable-solution'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/tasks/(?P<task_id>[0-9]+)/add-not-gradable-solution$',
        view=SubmitNonGradableSolutionView.as_view(),
        name='add-not-gradable-solution'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/tasks/(?P<task_id>[0-9]+)/solutions/(?P<solution_id>[0-9]+)/$',
        view=StudentSolutionDetailView.as_view(),
        name='student-solution-detail'
    ),
    url(
        regex='^tasks/(?P<task_id>[0-9]+)/$',
        view=TaskDetailView.as_view(),
        name='task-detail'
    ),
    url(
        regex='^materials/(?P<material_id>[0-9]+)/$',
        view=MaterialDetailView.as_view(),
        name='material-detail'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/tasks/(?P<task_id>[0-9]+)/all-students-solutions/$',
        view=AllStudentsSolutionsView.as_view(),
        name='all-students-solutions'
    ),
]