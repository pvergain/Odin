from django import forms

from captcha.fields import ReCaptchaField
from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm


class SignUpWithReCaptchaForm(SignupForm):
    captcha = ReCaptchaField(label='', attrs={'theme': 'clean'})


class OnboardingForm(SocialSignupForm):
    def __init__(self, *args, **kwargs):
        email_address = kwargs.pop('email_address')
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = email_address

    captcha = ReCaptchaField(label='', attrs={'theme': 'clean'})
    password = forms.CharField(widget=forms.PasswordInput())
