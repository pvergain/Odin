from typing import Dict, Set

from django.db.models import Q
from django.conf import settings

from .models import Solution, Student, Course, Week


def get_passed_and_failed_tasks(solution_data: Dict) -> Dict:
    """
    Fills up a dictionary with the status of tasks:
        "Passed" when a task has a passing solution, i.e. when a solution's status is Solution.OK
        "Failed" when a task has no passing solution
    """
    passed_or_failed = {}
    for task, solutions in solution_data.items():
        if task.gradable:
            for solution in solutions:
                if solution.status == Solution.OK:
                    passed_or_failed[task.name] = settings.TASK_PASSED
            if not passed_or_failed.get(task.name):
                passed_or_failed[task.name] = settings.TASK_FAILED
        else:
            for solution in solutions:
                if solution.status == Solution.SUBMITTED_WITHOUT_GRADING:
                    passed_or_failed[task.name] = settings.TASK_PASSED
            if not passed_or_failed[task.name]:
                passed_or_failed[task.name] = settings.TASK_FAILED

    return passed_or_failed


def get_solution_data(course: Course, student: Student) -> (Dict, Dict):
    """
    Fetch all of `student` solutions for `course` tasks and group them by task
    Get passed and failed tasks and then return the data
    """
    all_solutions = student.solutions.filter(task__course=course).prefetch_related('task')
    solution_data = {}
    for solution in all_solutions:
        task_solutions = solution_data.get(solution.task)
        if task_solutions:
            solution_data[solution.task].append(solution)
        else:
            solution_data[solution.task] = [solution]

    passed_and_failed = get_passed_and_failed_tasks(solution_data)

    return solution_data, passed_and_failed


def map_lecture_dates_to_week_days(course: Course) -> (Set, Dict):
    schedule = {}
    weekdays_with_lectures = set()
    weeks = Week.objects.filter(course=course).prefetch_related('lectures').order_by('id')
    for week in weeks:
        schedule[week.number] = {}
        lectures = week.lectures.all()

        if not lectures.exists():
            continue

        for lecture in lectures:
            schedule[week.number][lecture.date.weekday()] = {
                'lecture_date': lecture.date,
                'lecture_id': lecture.id
            }
            weekdays_with_lectures.add(lecture.date.weekday())

    weekdays_with_lectures = sorted(list(weekdays_with_lectures))

    return weekdays_with_lectures, schedule


def get_all_solved_student_solution_count_for_course(course: Course) -> Dict:
    q_expression = Q(task__gradable=True, status=2) | Q(task__gradable=False, status=6)
    all_passed_solutions = Solution.objects.filter(
        q_expression, task__course=course
    ).order_by('task').distinct('task').prefetch_related('student')

    students_passed_solutions_count = {}
    for solution in all_passed_solutions:
        solutions_for_student = students_passed_solutions_count.get(solution.student.email)
        if solutions_for_student:
            students_passed_solutions_count[solution.student.email] += 1
        else:
            students_passed_solutions_count[solution.student.email] = 1

    return students_passed_solutions_count
