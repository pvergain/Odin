from django.conf.urls import url

from .views import UserCoursesView, CourseDetailView

urlpatterns = [
    url(regex='^my-courses/$',
        view=UserCoursesView.as_view(),
        name='user-courses'),
    url(regex='^my-courses/(?P<pk>[0-9]+)/$',
        view=CourseDetailView.as_view(),
        name='user-course-detail'),

]
