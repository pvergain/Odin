from django.conf.urls import url

from .views import CreateApplicationInfoView, EditApplicationInfoView, CreateIncludedApplicationTaskView

urlpatterns = [
    url(regex='^(?P<course_id>[0-9]+)/create-application-info/$',
        view=CreateApplicationInfoView.as_view(),
        name='create-application-info'),
    url(regex='^(?P<course_id>[0-9]+)/edit-application-info/$',
        view=EditApplicationInfoView.as_view(),
        name='edit-application-info'),
    url(regex='^(?P<course_id>[0-9]+)/add-application-task/$',
        view=CreateIncludedApplicationTaskView.as_view(),
        name='add-application-task'),
]
