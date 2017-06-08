from django import forms

from captcha.fields import ReCaptchaField
from allauth.account.forms import SignupForm


class SignUpWithReCaptchaForm(SignupForm):
    captcha = ReCaptchaField(label='', attrs={'theme': 'clean'})
