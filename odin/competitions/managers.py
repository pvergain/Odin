from django.apps import apps
from django.core.exceptions import ValidationError

from odin.users.models import BaseUser
from odin.education.managers import BaseEducationUserManager


class CompetitionParticipantManager(BaseEducationUserManager):
    def create_from_user(self, user: BaseUser):
        CompetitionParticipant = apps.get_model('competitions', 'CompetitionParticipant')

        if user.downcast(CompetitionParticipant) is not None:
            raise ValidationError('Participant already exists')

        user._state.adding = False

        if not user.is_active:
            user.is_active = True
            user.save()

        participant = CompetitionParticipant(user_id=user.id)
        participant.__dict__.update(user.__dict__)

        participant.save()

        return CompetitionParticipant.objects.get(id=participant.id)


class CompetitionJudgeManager(BaseEducationUserManager):
    def create_from_user(self, user: BaseUser):
        CompetitionJudge = apps.get_model('competitions', 'CompetitionJudge')

        if user.downcast(CompetitionJudge) is not None:
            raise ValidationError('Judge already exists')

        user._state.adding = False

        if not user.is_active:
            user.is_active = True
            user.save()

        judge = CompetitionJudge(user_id=user.id)
        judge.__dict__.update(user.__dict__)

        judge.save()

        return CompetitionJudge.objects.get(id=judge.id)
