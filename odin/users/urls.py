from django.conf.urls import url

from .views import PersonalProfileView, UserProfileView

urlpatterns = [
    url(
        regex='^profile/(?P<user_email>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)/$',
        view=UserProfileView.as_view(),
        name='profile-by-email'),
    url(
        regex='^profile/$',
        view=PersonalProfileView.as_view(),
        name='profile'),
]
