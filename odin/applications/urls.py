from django.conf.urls import url

from .views import CreateApplicationInfoView

urlpatterns = [
    url(regex='^(?P<course_id>[0-9]+)/create-application-info/$',
        view=CreateApplicationInfoView.as_view(),
        name='create-application-info'),
]
