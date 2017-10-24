from django import forms

from odin.users.models import BaseUser

from odin.education.models import Student, Course, Teacher
from odin.interviews.models import Interviewer
from odin.competitions.models import Competition, CompetitionParticipant, CompetitionJudge


class DateInput(forms.DateInput):
    input_type = 'date'


class ManagementAddCourseForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Course
        fields = (
            'name',
            'start_date',
            'end_date',
            'attendable',
            'repository',
            'video_channel',
            'facebook_group',
            'slug_url',
            'public',
            'logo'
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


class AddParticipantToCompetitionForm(forms.Form):
    use_required_attribute = False

    participant = forms.ModelChoiceField(queryset=CompetitionParticipant.objects.all())
    competition = forms.ModelChoiceField(queryset=Competition.objects.all())


class AddTeacherToCourseForm(forms.Form):
    use_required_attribute = False

    teacher = forms.ModelChoiceField(queryset=Teacher.objects.all())
    course = forms.ModelChoiceField(queryset=Course.objects.all())


class AddJudgeToCompetitionForm(forms.Form):
    use_required_attribute = False

    judge = forms.ModelChoiceField(queryset=CompetitionJudge.objects.all())
    competition = forms.ModelChoiceField(queryset=Competition.objects.all())


class AddCourseToInterviewerCoursesForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.filter(application_info__isnull=False))
    interviewer = forms.ModelChoiceField(queryset=Interviewer.objects.all())
