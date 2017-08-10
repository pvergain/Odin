from django.conf.urls import url

from .views import ChooseInterviewView


urlpatterns = [
    url(r'^choose/(?P<application_id>[0-9]+)/(?P<interview_token>[-\w]+)/$',
        ChooseInterviewView.as_view(), name='choose_interview'),
]
