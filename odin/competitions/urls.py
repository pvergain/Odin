from django.conf.urls import url

from .views import UpdateApplicationCompetitionSolutionsView


urlpatterns = [
    url(
        regex=r'update-application-competition-solutions/$',
        view=UpdateApplicationCompetitionSolutionsView.as_view(),
        name='update-application-competition-solutions'
    )
]
