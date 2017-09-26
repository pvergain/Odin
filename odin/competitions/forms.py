from django import forms

from .models import CompetitionMaterial


class CompetitionMaterialFromExistingForm(forms.ModelForm):
    class Meta:
        model = CompetitionMaterial
        fields = ['competition', 'material']


class CompetitionMaterialModelForm(forms.ModelForm):
    class Meta:
        model = CompetitionMaterial
        fields = ['identifier', 'url', 'content', 'competition']
