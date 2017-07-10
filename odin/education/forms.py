from django import forms

from .models import (
    Course,
    Topic,
    IncludedMaterial,
    Week,
    IncludedTask,
    SourceCodeTest,
    BinaryFileTest
)


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
    def __init__(self, course, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['week'] = forms.ModelChoiceField(
            queryset=Week.objects.filter(course=course)
        )

    class Meta:
        model = Topic
        fields = ('name', )


class IncludedMaterialModelForm(forms.ModelForm):
    def __init__(self, course, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topic'] = forms.ModelChoiceField(
            queryset=Topic.objects.filter(course=course)
        )

    class Meta:
        model = IncludedMaterial
        fields = ('identifier', 'url', 'content')


class IncludedMaterialFromExistingForm(forms.ModelForm):
    class Meta:
        model = IncludedMaterial
        fields = ('topic', 'material')


class IncludedTaskModelForm(forms.ModelForm):
    def __init__(self, course, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topic'] = forms.ModelChoiceField(
            queryset=Topic.objects.filter(course=course)
        )

    class Meta:
        model = IncludedTask
        fields = ('name', 'description', 'gradable')
        widgets = {
            'gradable': forms.RadioSelect(choices=[(True, "is gradable"), (False, "is not gradable")])
        }


class IncludedTaskFromExistingForm(forms.ModelForm):
    def __init__(self, course=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if course:
            self.fields['topic'] = forms.ModelChoiceField(
                queryset=Topic.objects.filter(course=course)
            )

    class Meta:
        model = IncludedTask
        fields = ('topic', 'task')


class SourceCodeTestForm(forms.ModelForm):
    class Meta:
        model = SourceCodeTest
        fields = ('language', 'task', 'code')


class BinaryFileTestForm(forms.ModelForm):
    class Meta:
        model = BinaryFileTest
        exclude = ('language', 'task', 'file')
