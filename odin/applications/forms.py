from django import forms

from .models import ApplicationInfo


class DateInput(forms.DateInput):
    input_type = 'date'


class ApplicationInfoModelForm(forms.ModelForm):
    class Meta:
        model = ApplicationInfo
        fields = '__all__'

        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
            'start_interview_date': DateInput(),
            'end_interview_date': DateInput()
        }
