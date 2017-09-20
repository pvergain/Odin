import filecmp
from collections import deque

from django.core.management.base import BaseCommand, CommandError

from odin.education.models import Course, Solution


def compare_code_solutions(first_solution, second_solution):
    current_code, next_code = first_solution.code.strip('/n'), second_solution.code.strip('/n')
    comparison = current_code == next_code

    if comparison:
        print(
            f"""
             Matching contents in solutions
             {first_solution} from {first_solution.student.email} and
             {second_solution} from {second_solution.student.email}
             on task {first_solution.task.name}
             """
        )


def compare_file_solutions(first_solution, second_solution):
    current_filepath, next_filepath = first_solution.file.path, second_solution.file.path
    comparison = filecmp.cmp(current_filepath, next_filepath, shallow=False)

    if comparison:
        print(
            f"""
             Matching contents in files
             {current_filepath} from {first_solution.student.email} and
             {next_filepath} from {second_solution.student.email}
             on Task: {first_solution.task.name}
             """
        )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('course_id', nargs="+", type=int)

    def handle(self, *args, **options):
        for course_id in options['course_id']:
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                raise CommandError(f'Course with ID: {course_id} does not exist')

            topics = course.topics.all()
            for topic in topics:
                tasks = topic.tasks.all()

                for task in tasks:
                    if not task.gradable:
                        break

                    passing_solutions = deque(
                        task.solutions.filter(status=Solution.OK).order_by('student__email').distinct('student__email')
                    )

                    while passing_solutions:
                        current_solution = passing_solutions.popleft()
                        for next_solution in passing_solutions:
                            if task.test.is_source():
                                compare_code_solutions(current_solution, next_solution)
                            else:
                                compare_file_solutions(current_solution, next_solution)
