from captcha.fields import ReCaptchaField

from django import forms

from odin.education.models import ProgrammingLanguage

from .models import CompetitionMaterial, CompetitionTask, Competition


class DateInput(forms.DateInput):
    input_type = 'date'


class CreateCompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ('name', 'start_date', 'end_date', 'slug_url')
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }


class CompetitionMaterialFromExistingForm(forms.ModelForm):
    class Meta:
        model = CompetitionMaterial
        fields = ['competition', 'material']


class CompetitionMaterialModelForm(forms.ModelForm):
    class Meta:
        model = CompetitionMaterial
        fields = ['identifier', 'url', 'content', 'competition']


class CompetitionTaskModelForm(forms.ModelForm):
    language = forms.ModelChoiceField(
        queryset=ProgrammingLanguage.objects.all()
    )
    code = forms.CharField(
        widget=forms.Textarea(),
        required=False
    )
    file = forms.FileField(required=False)

    class Meta:
        model = CompetitionTask
        fields = ['competition', 'name', 'description', 'gradable']


class CompetitionTaskFromExistingForm(forms.ModelForm):
    class Meta:
        model = CompetitionTask
        fields = ['competition', 'task']


class CompetitionRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=255)
    email = forms.EmailField()

    captcha = ReCaptchaField(label='', attrs={'theme': 'clean'})


class CompetitionSetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    registration_token = forms.UUIDField()
    competition_slug = forms.SlugField()
