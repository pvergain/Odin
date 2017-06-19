from django.urls import reverse_lazy
from django.shortcuts import redirect

from django.contrib.auth.mixins import LoginRequiredMixin

from allauth.account import views as auth_views
from allauth.socialaccount import views as socialauth_views

from odin.users.models import BaseUser
from odin.common.utils import get_gh_email_address

from odin.common.mixins import ReadableFormErrorsMixin

from .forms import SignUpWithReCaptchaForm, OnboardingForm, PasswordResetForm


class LoginWrapperView(ReadableFormErrorsMixin, auth_views.LoginView):
    template_name = 'authentication/login.html'
    success_url = reverse_lazy('dashboard:users:profile')


class SignUpWrapperView(ReadableFormErrorsMixin, auth_views.SignupView):
    template_name = 'authentication/signup.html'
    form_class = SignUpWithReCaptchaForm
    success_url = reverse_lazy('account_email_verification_sent')


class LogoutWrapperView(LoginRequiredMixin, auth_views.LogoutView):
    template_name = 'authentication/logout.html'
    success_url = reverse_lazy('account_login')


class PasswordSetWrapperView(LoginRequiredMixin, auth_views.PasswordSetView):
    template_name = 'authentication/password_set.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('dashboard:users:profile')


class PasswordChangeWrapperView(LoginRequiredMixin, auth_views.PasswordChangeView):
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('dashboard:users:profile')


class PasswordResetWrapperView(ReadableFormErrorsMixin, auth_views.PasswordResetView):
    template_name = 'authentication/password_reset.html'


class PasswordResetDoneWrapperView(auth_views.PasswordResetDoneView):
    template_name = 'authentication/email_confirm_msg.html'


class PasswordResetFromKeyWrapperView(ReadableFormErrorsMixin, auth_views.PasswordResetFromKeyView):
    template_name = 'authentication/password_reset_from_key.html'
    success_url = reverse_lazy('account_login')
    form_class = PasswordResetForm


class PasswordResetFromKeyDoneWrapperView(auth_views.PasswordResetFromKeyDoneView):
    pass


class AccountInactiveWrapperView(auth_views.AccountInactiveView):
    pass


class SocialConnectionsWrapperView(LoginRequiredMixin, socialauth_views.ConnectionsView):
    template_name = 'authentication/connections.html'


class SocialSignupWrapperView(ReadableFormErrorsMixin, socialauth_views.SignupView):
    form_class = OnboardingForm
    success_url = reverse_lazy('account_email_verification_sent')
    template_name = 'authentication/onboarding.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        email_address = get_gh_email_address(self.request)
        kwargs['email_address'] = email_address
        return kwargs

    def form_valid(self, form):
        super().form_valid(form)
        user = BaseUser.objects.get(email=form.cleaned_data.get('email'))
        user.set_password(form.cleaned_data['password'])
        user.save()
        return redirect(self.success_url)


class EmailVerificationSentWrapperView(auth_views.EmailVerificationSentView):
    template_name = 'authentication/email_confirm_msg.html'
