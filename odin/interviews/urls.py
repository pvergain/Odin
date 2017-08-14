from django.conf.urls import url

from .views import ChooseInterviewView, InterviewsListView, GenerateInterviewsView


urlpatterns = [
    url(
        regex='^choose/(?P<application_id>[0-9]+)/(?P<interview_token>[-\w]+)/$',
        view=ChooseInterviewView.as_view(),
        name='choose-interview'
    ),
    url(
        regex='^$',
        view=InterviewsListView.as_view(),
        name='user-interviews'
    ),
    url(
        regex='^generate-interviews/$',
        view=GenerateInterviewsView.as_view(),
        name='do-it'
    ),

]
