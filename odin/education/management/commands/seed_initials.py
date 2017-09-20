from django.core.management.base import BaseCommand
from django.core.management import call_command

from odin.education.models import Course, Student, Teacher


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Course.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()

        call_command('seed_with_competition')
        call_command('seed_courses')
