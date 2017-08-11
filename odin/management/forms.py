from django import forms

from odin.users.models import BaseUser

from odin.interviews.models import Interviewer
from odin.education.models import Student, Course, Teacher


class DateInput(forms.DateInput):
    input_type = 'date'


class ManagementAddCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'name',
            'start_date',
            'end_date',
            'repository',
            'video_channel',
            'facebook_group',
            'slug_url',
            'public',
        )
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }


class ManagementAddUserForm(forms.ModelForm):
    class Meta:
        model = BaseUser
        fields = ('email', )


class AddStudentToCourseForm(forms.Form):
    use_required_attribute = False

    student = forms.ModelChoiceField(queryset=Student.objects.all())
    course = forms.ModelChoiceField(queryset=Course.objects.all())


class AddTeacherToCourseForm(forms.Form):
    use_required_attribute = False

    teacher = forms.ModelChoiceField(queryset=Teacher.objects.all())
    course = forms.ModelChoiceField(queryset=Course.objects.all())


class AddCourseToInterviewerCoursesForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.filter(application_info__isnull=False))
    interviewer = forms.ModelChoiceField(queryset=Interviewer.objects.all())
