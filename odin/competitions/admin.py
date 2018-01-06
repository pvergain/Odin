from django.contrib import admin


from odin.competitions.models import (
    Competition,
    CompetitionTask
)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    pass


@admin.register(CompetitionTask)
class CompetitionTaskAdmin(admin.ModelAdmin):
    pass
