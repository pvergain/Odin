from django.conf.urls import url

from .views import (
    CreateCompetitionView,
    EditCompetitionView,
    CreateCompetitionMaterialFromExistingView,
    CreateNewCompetitionMaterialView,
    EditCompetitionMaterialView,
    CompetitionDetailView,
    CreateNewCompetitionTaskView
)

urlpatterns = [
    url(
        regex='create-competition/$',
        view=CreateCompetitionView.as_view(),
        name='create-competition'
    ),
    url(
        regex='^(?P<competition_slug>[-\w]+)/$',
        view=CompetitionDetailView.as_view(),
        name='competition-detail'
    ),
    url(
        regex='^edit-competition/(?P<competition_slug>[-\w]+)/$',
        view=EditCompetitionView.as_view(),
        name='edit-competition'
    ),
    url(
        regex='^(?P<competition_slug>[-\w]+)/create-material/from-existing/$',
        view=CreateCompetitionMaterialFromExistingView.as_view(),
        name='create-competition-material-from-existing'
    ),
    url(
        regex='(?P<competition_slug>[-\w]+)/create-material/new/$',
        view=CreateNewCompetitionMaterialView.as_view(),
        name='create-new-competition-material'
    ),
    url(
        regex='(?P<competition_slug>[-\w]+)/edit-material/(?P<material_id>[0-9]+)/$',
        view=EditCompetitionMaterialView.as_view(),
        name='edit-competition-material'
    ),
    url(
        regex='(?P<competition_slug>[-\w]+)/create-task/new/$',
        view=CreateNewCompetitionTaskView.as_view(),
        name='create-new-competition-task'
    )
]
