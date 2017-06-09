from django.urls import reverse_lazy
from django.views.generic import FormView
from django.shortcuts import redirect

from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from allauth.account import views as auth_views
from allauth.socialaccount import views as socialauth_views

from .forms import SignUpWithReCaptchaForm, OnboardingForm
from .models import BaseUser

from allauth.socialaccount.providers import base
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from allauth.socialaccount.providers.github import views, urls, models, provider
from allauth.socialaccount.providers.oauth2 import views, urls, provider


class TestView(FormView):
    form_class = OnboardingForm
    template_name = 'users/onboarding.'

    def form_valid(self, form):
        form.instance.current_email = self.kwargs['current_email']
        return super().form_valid(form)


class LoginWrapperView(auth_views.LoginView):
    template_name = 'users/login.html'
    success_url = reverse_lazy('education:sample-profile')


account_login = LoginWrapperView.as_view()


class SignUpWrapperView(auth_views.SignupView):
    template_name = 'users/signup.html'
    form_class = SignUpWithReCaptchaForm
    success_url = reverse_lazy('account_login')


account_signup = SignUpWrapperView.as_view()


class LogoutWrapperView(LoginRequiredMixin, auth_views.LogoutView):
    template_name = 'users/logout.html'
    success_url = reverse_lazy('account_login')


account_logout = LogoutWrapperView.as_view()


class PasswordSetWrapperView(LoginRequiredMixin, auth_views.PasswordSetView):
    template_name = 'users/password_set.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('education:sample-profile')


password_set = PasswordSetWrapperView.as_view()


class PasswordChangeWrapperView(LoginRequiredMixin, auth_views.PasswordChangeView):
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('education:sample-profile')


password_change = PasswordChangeWrapperView.as_view()


class PasswordResetWrapperView(auth_views.PasswordResetView):
    template_name = 'users/password_reset.html'


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


class SocialConnectionsWrapperView(LoginRequiredMixin, socialauth_views.ConnectionsView):
    pass


connections = SocialConnectionsWrapperView.as_view()


class SocialSignupWrapperView(socialauth_views.SignupView):
    form_class = OnboardingForm
    success_url = settings.LOGIN_URL

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        socialaccount = self.request.session.get('socialaccount_sociallogin', {})
        email_address = socialaccount.get('email_addresses', [{}])[0].get('email', '')
        kwargs['email_address'] = email_address
        return kwargs

    def form_valid(self, form):
        super().form_valid(form)
        user = BaseUser.objects.get(email=form.cleaned_data.get('email'))
        user.set_password(form.cleaned_data['password'])
        user.save()
        return redirect(self.success_url)


signup = SocialSignupWrapperView.as_view()
