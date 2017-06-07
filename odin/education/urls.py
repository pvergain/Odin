from django.conf.urls import url
from .views import SampleProfileView

app_name = 'education'

urlpatterns = [
    url(r'^profile/$', SampleProfileView.as_view(), name='sample-profile'),
]
