from django.urls import reverse_lazy
from django.views.generic import FormView
from django.shortcuts import redirect

from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from allauth.account import views as auth_views
from allauth.socialaccount import views as socialauth_views

from .forms import SignUpWithReCaptchaForm, OnboardingForm
from .models import BaseUser


class OnboardingView(FormView):
    form_class = OnboardingForm
    template_name = 'users/onboarding.html'

    def form_valid(self, form):
        form.instance.current_email = self.kwargs['current_email']
        return super().form_valid(form)


class LoginWrapperView(auth_views.LoginView):
    template_name = 'users/login.html'
    success_url = reverse_lazy('education:sample-profile')


class SignUpWrapperView(auth_views.SignupView):
    template_name = 'users/signup.html'
    form_class = SignUpWithReCaptchaForm
    success_url = reverse_lazy('account_login')


class LogoutWrapperView(LoginRequiredMixin, auth_views.LogoutView):
    template_name = 'users/logout.html'
    success_url = reverse_lazy('account_login')


class PasswordSetWrapperView(LoginRequiredMixin, auth_views.PasswordSetView):
    template_name = 'users/password_set.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('education:sample-profile')


class PasswordChangeWrapperView(LoginRequiredMixin, auth_views.PasswordChangeView):
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('education:sample-profile')


class PasswordResetWrapperView(auth_views.PasswordResetView):
    template_name = 'users/password_reset.html'


class PasswordResetDoneWrapperView(auth_views.PasswordResetDoneView):
    pass


class PasswordResetFromKeyWrapperView(auth_views.PasswordResetFromKeyView):
    pass


class PasswordResetFromKeyDoneWrapperView(auth_views.PasswordResetFromKeyDoneView):
    pass


class AccountInactiveWrapperView(auth_views.AccountInactiveView):
    pass


class SocialConnectionsWrapperView(LoginRequiredMixin, socialauth_views.ConnectionsView):
    pass


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
