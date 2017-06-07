from django.conf.urls import url
from .views import SampleProfileView


urlpatterns = [
    url(r'^profile/$', SampleProfileView.as_view(), name='sample-profile'),
]
