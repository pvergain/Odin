from django import forms

from captcha.fields import ReCaptchaField

from allauth.account.forms import SignupForm, SetPasswordField
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from allauth.account.adapter import get_adapter


class SignUpWithReCaptchaForm(SignupForm):
    captcha = ReCaptchaField(label='', attrs={'theme': 'clean'})


class OnboardingForm(SocialSignupForm):
    captcha = ReCaptchaField(label='', attrs={'theme': 'clean'})
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        email_address = kwargs.pop('email_address')

        super().__init__(*args, **kwargs)

        self.fields['email'].initial = email_address


class PasswordResetForm(forms.Form):
    password = SetPasswordField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.temp_key = kwargs.pop("temp_key", None)
        super().__init__(*args, **kwargs)
        self.fields['password'].user = self.user

    def save(self):
        get_adapter().set_password(self.user, self.cleaned_data['password'])
