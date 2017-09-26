from django.conf.urls import url

from .views import CreateCompetitionView, EditCompetitionView

urlpatterns = [
    url(
        regex='create-competition/$',
        view=CreateCompetitionView.as_view(),
        name='create-competition'
    ),
    url(
        regex='edit-competition/$',
        view=EditCompetitionView.as_view(),
        name='edit-competition'
    )
]
