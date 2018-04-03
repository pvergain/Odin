from django.contrib import admin

from .models import (
    GraderBinaryProblem,
    GraderPlainProblem,
)


@admin.register(GraderBinaryProblem)
class GraderBinaryProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(GraderPlainProblem)
class GraderPlainProblemAdmin(admin.ModelAdmin):
    pass
