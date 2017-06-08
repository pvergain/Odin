from django import forms

from captcha.fields import ReCaptchaField
from allauth.account.forms import SignupForm


class SignUpWithReCaptchaForm(SignupForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    captcha = ReCaptchaField(label='', attrs={'theme': 'clean'})
