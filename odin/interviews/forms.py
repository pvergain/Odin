from django import forms

from .models import Interview, InterviewerFreeTime


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class ChooseInterviewForm(forms.Form):
    interviews = forms.ModelChoiceField(
        queryset=Interview.objects.get_free_slots().order_by('date', 'start_time')
    )


class FreeTimeModelForm(forms.ModelForm):
    class Meta:
        model = InterviewerFreeTime

        fields = [
            'interviewer',
            'date',
            'start_time',
            'end_time',
            'buffer_time'
        ]

        widgets = {
            'date': DateInput(),
            'start_time': TimeInput(),
            'end_time': TimeInput()
        }
