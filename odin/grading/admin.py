from django.contrib import admin

from .models import (
    GraderBinaryProblem,
    GraderPlainProblem,
    GraderPlainProblemWithRequirements,
)


@admin.register(GraderBinaryProblem)
class GraderBinaryProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(GraderPlainProblem)
class GraderPlainProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(GraderPlainProblemWithRequirements)
class GraderPlainProblemWithRequirementsAdmin(admin.ModelAdmin):
    pass
