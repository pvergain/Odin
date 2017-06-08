from django.urls import reverse_lazy
from django.shortcuts import redirect

from allauth.account import views as auth_views
from allauth.socialaccount import views as socialauth_views
from allauth.socialaccount.templatetags import socialaccount


class LoginWrapperView(auth_views.LoginView):
    success_url = reverse_lazy('education:sample-profile')


account_login = LoginWrapperView.as_view()


class SignUpWrapperView(auth_views.SignupView):
    success_url = reverse_lazy('account_login')


account_signup = SignUpWrapperView.as_view()


class LogoutWrapperView(auth_views.LogoutView):
    success_url = reverse_lazy('account_login')


account_logout = LogoutWrapperView.as_view()


class PasswordSetWrapperView(auth_views.PasswordSetView):
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('education:sample-profile')


password_set = PasswordSetWrapperView.as_view()


class PasswordChangeWrapperView(auth_views.PasswordChangeView):
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('education:sample-profile')


password_change = PasswordChangeWrapperView.as_view()


class PasswordResetWrapperView(auth_views.PasswordResetView):
    pass


password_reset = PasswordResetWrapperView.as_view()


class PasswordResetDoneWrapperView(auth_views.PasswordResetDoneView):
    pass


password_reset_done = PasswordResetDoneWrapperView.as_view()


class PasswordResetFromKeyWrapperView(auth_views.PasswordResetFromKeyView):
    pass


password_reset_from_key = PasswordResetFromKeyWrapperView.as_view()


class PasswordResetFromKeyDoneWrapperView(auth_views.PasswordResetFromKeyDoneView):
    pass


password_reset_from_key_done = PasswordResetFromKeyDoneWrapperView.as_view()


class AccountInactiveWrapperView(auth_views.AccountInactiveView):
    pass


account_inactive = AccountInactiveWrapperView.as_view()


class SocialConnectionsWrapperView(socialauth_views.ConnectionsView):
    pass


connections = SocialConnectionsWrapperView.as_view()
