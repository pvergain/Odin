from django.conf.urls import url

from .views import UserCoursesView, CourseDetailView, PublicCourseListView, PublicCourseDetailView

urlpatterns = [
    url(regex='^my-courses/$',
        view=UserCoursesView.as_view(),
        name='user-courses'),
    url(regex='^my-courses/(?P<course_id>[0-9]+)/$',
        view=CourseDetailView.as_view(),
        name='user-course-detail'),
]


courses_public_urlpatterns = [
    url(regex='^$',
        view=PublicCourseListView.as_view(),
        name='courses'),
    url(regex='^(?P<course_slug>[-\w]+)/$',
        view=PublicCourseDetailView.as_view(),
        name='course_detail'),
]
