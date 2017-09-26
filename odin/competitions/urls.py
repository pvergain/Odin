from django.conf.urls import url

from .views import (
    CreateCompetitionView,
    EditCompetitionView,
    CreateCompetitionMaterialFromExistingView,
    CreateNewCompetitionMaterialView,
    EditCompetitionMaterialView
)

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
    ),
    url(
        regex='(?P<competition_slug>[-\w]+)/create-material/from-exististing/$',
        view=CreateCompetitionMaterialFromExistingView.as_view(),
        name='create-competition-material-from-existing'
    ),
    url(
        regex='(?P<competition_slug>[-\w]+)/create-material/new/$',
        view=CreateNewCompetitionMaterialView.as_view(),
        name='create-new-competition-material'
    ),
    url(
        regex='(?P<competition_slug>[-\w]+)/edit_material/(?P<material_id>[0-9]+)/$',
        view=EditCompetitionMaterialView.as_view(),
        name='edit-competition-material'
    )
]
