from django import forms

from .models import (
    Topic,
    IncludedMaterial,
    Week,
    IncludedTask,
    IncludedTest,
    Solution,
    ProgrammingLanguage
)


class TopicModelForm(forms.ModelForm):
    def __init__(self, course, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['week'] = forms.ModelChoiceField(
            queryset=Week.objects.filter(course=course).order_by('number')
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
    language = forms.ModelChoiceField(queryset=ProgrammingLanguage.objects.all(), required=False)
    code = forms.CharField(widget=forms.Textarea(), required=False)
    file = forms.FileField(required=False)

    def __init__(self, course, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topic'] = forms.ModelChoiceField(
            queryset=Topic.objects.filter(course=course)
        )

    class Meta:
        model = IncludedTask
        fields = ('name', 'description', 'gradable')
        widgets = {
            'gradable': forms.CheckboxInput()
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
        model = IncludedTest
        fields = ('language', 'task', 'code')


class BinaryFileTestForm(forms.ModelForm):
    class Meta:
        model = IncludedTest
        fields = ('language', 'task', 'file')


class SubmitGradableSolutionForm(forms.ModelForm):
    def __init__(self, is_test_source=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if is_test_source:
            self.fields['code'] = forms.CharField(widget=forms.Textarea)
        else:
            self.fields['file'] = forms.FileField()

    class Meta:
        model = Solution
        fields = []


class SubmitNonGradableSolutionForm(forms.ModelForm):
    url = forms.URLField(required=True)

    class Meta:
        model = Solution
        fields = ('url', )
