from django import forms

from captcha.fields import ReCaptchaField


class SignUpWithReCaptchaForm(forms.Form):
    captcha = ReCaptchaField(label='', attrs={'theme': 'light'})

    def signup(self, request, user):
        pass
