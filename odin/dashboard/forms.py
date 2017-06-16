from django import forms

from ..users.models import BaseUser


class ManagementAddUserForm(forms.ModelForm):
    class Meta:
        model = BaseUser
        fields = ('email', )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_unusable_password()
        instance.is_active = False
        if commit:
            instance.save()
        return instance
