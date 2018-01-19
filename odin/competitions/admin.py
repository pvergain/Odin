from django.contrib import admin


from odin.competitions.models import (
    Competition,
    CompetitionTask,
    CompetitionTest,
    Solution
)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    pass


@admin.register(CompetitionTask)
class CompetitionTaskAdmin(admin.ModelAdmin):
    pass


@admin.register(CompetitionTest)
class CompetitionTestAdmin(admin.ModelAdmin):
    pass


@admin.register(Solution)
class CompetitionSolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'participant')
