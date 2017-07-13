from django.conf.urls import url

from .views import SolutionsAPIView


urlpatterns = [
    url(r'^api/solution/$', SolutionsAPIView.as_view(), name='grade-solution'),
]
