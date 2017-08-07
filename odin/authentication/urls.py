from django.conf.urls import url

from allauth.urls import urlpatterns as allauth_urls

from .views import (
    LoginWrapperView,
    SignUpWrapperView,
    LogoutWrapperView,
    PasswordSetWrapperView,
    PasswordChangeWrapperView,
    PasswordResetWrapperView,
    SocialSignupWrapperView,
    PasswordResetDoneWrapperView,
    AccountInactiveWrapperView,
    PasswordResetFromKeyWrapperView,
    PasswordResetFromKeyDoneWrapperView,
    SocialConnectionsWrapperView,
    EmailVerificationSentWrapperView
    )


urlpatterns = [
    url(
        regex='^social/signup/$',
        view=SocialSignupWrapperView.as_view(),
        name='socialaccount_signup'
    ),
    url(
        regex='^login/$',
        view=LoginWrapperView.as_view(),
        name='account_login'
    ),
    url(
        regex='^signup/$',
        view=SignUpWrapperView.as_view(),
        name='account_signup'
    ),
    url(
        regex='^logout/$',
        view=LogoutWrapperView.as_view(),
        name='account_logout'
    ),
    url(
        regex='^password/set/$',
        view=PasswordSetWrapperView.as_view(),
        name='account_set_password'
    ),
    url(
        regex='^password/change/$',
        view=PasswordChangeWrapperView.as_view(),
        name='account_change_password'
    ),
    url(
        regex='^password/reset/$',
        view=PasswordResetWrapperView.as_view(),
        name='account_reset_password'
    ),
    url(
        regex='^social/connections/$',
        view=SocialConnectionsWrapperView.as_view(),
        name='socialaccount_connections'
    ),
    url(
        regex='^password/reset/done/$',
        view=PasswordResetDoneWrapperView.as_view(),
        name="account_reset_password_done"
    ),
    url(
        regex='^inactive/$',
        view=AccountInactiveWrapperView.as_view(),
        name="account_inactive"
    ),
    url(
        regex='^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
        view=PasswordResetFromKeyWrapperView.as_view(),
        name="account_reset_password_from_key"
    ),
    url(
        regex='^password/reset/key/done/$',
        view=PasswordResetFromKeyDoneWrapperView.as_view(),
        name="account_reset_password_from_key_done"),
    url(
        regex='^confirm-email/$',
        view=EmailVerificationSentWrapperView.as_view(),
        name='account_email_verification_sent'
    ),
] + allauth_urls
