from django import template

register = template.Library()


@register.filter(name='has_solution_for_task')
def has_solution_for_task(task, application):
    queryset = task.solutions.filter(participant=application.user)

    return queryset.exists()
