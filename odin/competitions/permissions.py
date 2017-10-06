from rest_framework.permissions import BasePermission

from odin.common.mixins import BaseUserPassesTestMixin


class IsParticipantOrJudgeInCompetitionPermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        competition = self.competition
        email = self.request.user.email
        is_participant = competition.participants.filter(email=email).exists()
        is_judge = self.competition.judges.filter(email=email).exists()

        if is_participant or is_judge:
            return True and super().test_func()

        return False


class IsParticipantInCompetitionPermission(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        competition = self.competition
        email = self.request.user.email
        is_participant = competition.participants.filter(email=email).exists()

        if is_participant:
            return True and super().test_func()

        return False


class IsJudgeInCompetitionPermisssion(BaseUserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        competition = self.competition
        email = self.request.user.email
        is_judge = competition.judges.filter(email=email).exists()

        if is_judge:
            return True and super().test_func()

        return False


class IsParticipantInCompetitionApiPerimission(BasePermission):
    message = "Need to be a participant in this competition"

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        email = request.user.email
        is_participant = view.competition.participants.filter(email=email).exists()

        if is_participant:
            return True

        return False


class IsParticipantOrJudgeInCompetitionApiPermission(BasePermission):
    message = 'Need to be participant or judge in this competition'

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        competition = view.get_object().task.competition
        email = request.user.email

        is_judge = competition.judges.filter(email=email).exists()
        is_solution_author = False

        if hasattr(request.user, 'competitionparticipant'):
            is_solution_author = view.get_object().participant = request.user.competitionparticipant
        if is_solution_author or is_judge:
            return True

        return False


class IsStandaloneCompetitionPermission(BasePermission):
    raise_exception = True

    def test_func(self):
        if self.competition.is_application_competition:
            return False

        return True and super().test_func()
