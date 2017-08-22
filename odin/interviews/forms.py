from django import forms

from .models import InterviewerFreeTime


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class FreeTimeModelForm(forms.ModelForm):
    class Meta:
        model = InterviewerFreeTime

        fields = [
            'interviewer',
            'date',
            'start_time',
            'end_time',
            'interview_time_length',
            'break_time'
        ]

        widgets = {
            'date': DateInput(),
            'start_time': TimeInput(),
            'end_time': TimeInput()
        }
