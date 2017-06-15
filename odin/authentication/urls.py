from django.conf.urls import url

from allauth.urls import urlpatterns as allauth_urls

from .views import (LoginWrapperView, SignUpWrapperView, LogoutWrapperView, PasswordSetWrapperView,
                    PasswordChangeWrapperView, PasswordResetWrapperView, SocialSignupWrapperView,
                    PasswordResetDoneWrapperView, AccountInactiveWrapperView,
                    PasswordResetFromKeyWrapperView, PasswordResetFromKeyDoneWrapperView,
                    SocialConnectionsWrapperView, EmailVerificationSentWrapperView)


urlpatterns = [
    url(r'^social/signup/$', SocialSignupWrapperView.as_view(), name='socialaccount_signup'),
    url(r'^login/$', LoginWrapperView.as_view(), name='account_login'),
    url(r'^signup/$', SignUpWrapperView.as_view(), name='account_signup'),
    url(r'^logout/$', LogoutWrapperView.as_view(), name='account_logout'),
    url(r'^password/set/$', PasswordSetWrapperView.as_view(), name='account_set_password'),
    url(r'^password/change/$', PasswordChangeWrapperView.as_view(), name='account_change_password'),
    url(r'^password/reset/$', PasswordResetWrapperView.as_view(), name='account_reset_password'),
    url(r'^social/connections/$', SocialConnectionsWrapperView.as_view(), name='socialaccount_connections'),
    url(r'^password/reset/done/$', PasswordResetDoneWrapperView.as_view(), name="account_reset_password_done"),
    url(r'^inactive/$', AccountInactiveWrapperView.as_view(), name="account_inactive"),
    url(r'^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$', PasswordResetFromKeyWrapperView.as_view(),
        name="account_reset_password_from_key"),
    url(r'^password/reset/key/done/$', PasswordResetFromKeyDoneWrapperView.as_view(),
        name="account_reset_password_from_key_done"),
    url(r'^confirm-email/$', EmailVerificationSentWrapperView.as_view(), name='account_email_verification_sent')
] + allauth_urls
