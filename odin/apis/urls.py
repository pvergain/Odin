from django.conf.urls import include, url

urlpatterns = [
    url(
        regex='^education/',
        view=include('odin.education.apis.urls', namespace='education')
    ),
    url(
        regex='^auth/',
        view=include('odin.authentication.apis.urls', namespace='auth')
    )
]
