from django.conf.urls import url

from .views import (
    CreateApplicationInfoView,
    EditApplicationInfoView,
    ApplyToCourseView,
    UserApplicationsListView,
    ApplicationDetailView,
    EditApplicationView
)

urlpatterns = [
    url(
        regex='^(?P<course_id>[0-9]+)/create-application-info/$',
        view=CreateApplicationInfoView.as_view(),
        name='create-application-info'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/edit-application-info/$',
        view=EditApplicationInfoView.as_view(),
        name='edit-application-info'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/apply/$',
        view=ApplyToCourseView.as_view(),
        name='apply-to-course'
    ),
    url(
        regex='^user-applications/$',
        view=UserApplicationsListView.as_view(),
        name='user-applications'
    ),
    url(
        regex='^application-details/(?P<application_id>[0-9]+)$',
        view=ApplicationDetailView.as_view(),
        name='application-detail'
    ),
    url(
        regex='^(?P<course_id>[0-9]+)/edit-application/$',
        view=EditApplicationView.as_view(),
        name='edit-application'
    )
]
