from django import forms

from .models import Interview


class ChooseInterviewForm(forms.Form):
    interviews = forms.ModelChoiceField(
        queryset=Interview.objects.get_free_slots().order_by('date', 'start_time')
    )
