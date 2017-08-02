from django import forms

from .models import ApplicationInfo, IncludedApplicationTask, Application


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


class IncludedApplicationTaskForm(forms.ModelForm):
    class Meta:
        model = IncludedApplicationTask
        fields = [
            'name',
            'description',
            'application_info'
        ]


class IncludedApplicationTaskFromExistingForm(forms.ModelForm):
    class Meta:
        model = IncludedApplicationTask
        fields = ['task', 'application_info']


class ApplicationCreateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'application_info',
            'user',
            'phone',
            'skype',
            'works_at',
            'studies_at',
        ]


class ApplicationEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance.application_info, 'tasks'):
            for task in self.instance.application_info.tasks.all():
                self.fields[task.name] = forms.URLField(label=task.name, required=False)

    class Meta:
        model = Application
        fields = [
            'application_info',
            'user',
            'phone',
            'skype',
            'works_at',
            'studies_at',
        ]
