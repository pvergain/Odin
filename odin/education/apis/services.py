from odin.education.models import Student
from typing import List


def get_all_course_assignments_per_student(*, student: Student):
    assignments = [assignment for assignment in student.course_assignments.all()]
    return assignments


def get_all_topics_for_courses_of_a_student(*, course_assignments_per_student: List):
    all_topics = []
    for assignment in course_assignments_per_student:
        if assignment.course.has_started and not assignment.course.has_finished:
            all_topics.append([topic for topic in assignment.course.topics.all()])

    return all_topics


def get_gradable_tasks_per_course(*, all_topics: List) -> List[List]:
    gradable_tasks = {}
    for topic_list in all_topics:
        for topic in topic_list:
            for task in topic.tasks.all():
                if task.gradable:
                    if task.topic.course.id not in gradable_tasks.keys():
                        gradable_tasks[task.topic.course.name] = [task.id]
                    else:
                        gradable_tasks[task.topic.course.name].append(task.id)

    return gradable_tasks
