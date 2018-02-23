from django import template

register = template.Library()


@register.filter(name='has_solution_for_task')
def has_solution_for_task(task, application):
    queryset = task.solutions.filter(participant=application.user)

    return queryset.exists()

@register.filter(name='is_equal')
def equals(item1, item2):
    if item1 == None:
        par1 = ''
    else:
        par1 = str(item1.lower())
    if item2 == None:
        par2 = ''
    else:
        par2 = str(item2.lower())
    return par1 == par2