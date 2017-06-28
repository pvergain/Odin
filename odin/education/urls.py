from django.conf.urls import url, include

from .views import (
    UserCoursesView,
    CourseDetailView,
    PublicCourseListView,
    PublicCourseDetailView,
    AddTopicToCourseView,
    AddNewIncludedMaterialView,
    AddIncludedMaterialFromExistingView
)


courses_public_urlpatterns = [
    url(regex='^$',
        view=PublicCourseListView.as_view(),
        name='courses'),
    url(regex='^(?P<course_slug>[-\w]+)/$',
        view=PublicCourseDetailView.as_view(),
        name='course_detail'),
]

course_management_urlpatterns = [
    url(regex='^(?P<course_id>[0-9]+)/add-topic/$',
        view=AddTopicToCourseView.as_view(),
        name='manage-course-topics'),
    url(regex='^(?P<course_id>[0-9]+)/(?P<topic_id>[0-9]+)/add-material/$',
        view=AddIncludedMaterialFromExistingView.as_view(),
        name='add-included-material-from-existing'),
    url(regex='^(?P<course_id>[0-9]+)/(?P<topic_id>[0-9]+)/add-material/new$',
        view=AddNewIncludedMaterialView.as_view(),
        name='add-new-included-material'),
]

urlpatterns = [
    url(regex='^my-courses/$',
        view=UserCoursesView.as_view(),
        name='user-courses'),
    url(regex='^my-courses/(?P<course_id>[0-9]+)/$',
        view=CourseDetailView.as_view(),
        name='user-course-detail'),
    url(regex='^manage-course/',
        view=include(course_management_urlpatterns,
                     namespace='course-management')),
]
