from django import forms

from .models import Course, Topic, IncludedMaterial


class DateInput(forms.DateInput):
    input_type = 'date'


class ManagementAddCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name', 'start_date', 'end_date', 'repository', 'video_channel', 'facebook_group', 'slug_url')
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }


class TopicModelForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('name', 'week')


class IncludedMaterialModelForm(forms.ModelForm):
    class Meta:
        model = IncludedMaterial
        fields = ('identifier', 'url', 'content', 'topic')


class IncludedMaterialFromExistingForm(forms.ModelForm):
    class Meta:
        model = IncludedMaterial
        fields = ('topic', 'material')
