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


class IsParticipantIncCompetitionPermission(BaseUserPassesTestMixin):
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
