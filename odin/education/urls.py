from django.conf.urls import url
from .views import ProfileView

app_name = 'education'

urlpatterns = [
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
]
