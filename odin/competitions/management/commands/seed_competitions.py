from queue import deque
from random import choice

from django.core.management import BaseCommand

from odin.applications.factories import ApplicationInfoFactory, ApplicationFactory

from odin.competitions.factories import (
    CompetitionFactory,
    CompetitionTaskFactory,
    CompetitionMaterialFactory,
    CompetitionParticipantFactory,
    CompetitionJudgeFactory,
)

COMPETITION_DATA = (("Hack Competition", "hack-competition"), ("HackConf Competition", "hackconf-competition"))


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        competitions = [CompetitionFactory(name=name, slug_url=slug)
                        for (name, slug) in COMPETITION_DATA]
        competition_app_info = ApplicationInfoFactory(competition=choice(competitions))
        ApplicationFactory(application_info=competition_app_info)

        participants = deque(CompetitionParticipantFactory.create_batch(10))
        judges = deque(CompetitionJudgeFactory.create_batch(6))

        while participants:
            selected_competition = choice(competitions)
            selected_competition.participants.add(participants.popleft())
            selected_competition.save()

        while judges:
            selected_competition = choice(competitions)
            selected_competition.judges.add(judges.popleft())
            selected_competition.save()

        for competition in competitions:
            CompetitionTaskFactory(competition=competition)
            CompetitionMaterialFactory(competition=competition)
