from django.contrib import admin

from odin.applications.models import Application, ApplicationInfo


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'application_info', 'is_partially_completed',
                    'phone', 'skype', 'works_at', 'studies_at')


@admin.register(ApplicationInfo)
class ApplicationInfoAdmin(admin.ModelAdmin):
    pass
