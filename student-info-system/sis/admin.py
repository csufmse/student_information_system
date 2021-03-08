from django.contrib import admin

from .models import Person, Semester


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_registration_opens', 'date_started',
                    'date_last_drop', 'date_ended')


admin.site.register(Semester, SemesterAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_admin', 'is_active',
                    'is_semester_admin', 'is_class_admin', 'is_grade_editor')


admin.site.register(Person, PersonAdmin)
