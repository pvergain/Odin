from django import forms

from odin.users.models import BaseUser


class ManagementAddUserForm(forms.ModelForm):
    class Meta:
        model = BaseUser
        fields = ('email', )
