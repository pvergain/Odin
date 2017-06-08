from django.conf.urls import url

from allauth.urls import urlpatterns as allauth_urls
from allauth.account import urls

from . import views


urlpatterns = [
    url(r'^login/$', views.account_login, name='account_login'),
    url(r'^signup/$', views.account_signup, name='account_signup'),
    url(r'^logout/$', views.account_logout, name='account_logout'),
    url(r'^password/set/$', views.password_set, name='account_set_password'),
    url(r'^password/change/$', views.password_change, name='account_change_password'),
    url(r'^password/reset/$', views.password_reset, name='account_reset_password'),
    url(r'^social-connections/$', views.connections, name='socialaccount_connections'),
    url(r'^password/reset/done/$', views.password_reset_done, name="account_reset_password_done"),
    url(r'^inactive/$', views.account_inactive, name="account_inactive"),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", views.password_reset_from_key,
        name="account_reset_password_from_key"),
    url(r"^password/reset/key/done/$", views.password_reset_from_key_done,
        name="account_reset_password_from_key_done"),
] + allauth_urls
