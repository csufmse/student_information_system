from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Person, Semester, Department, Major, Course, Section


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_registration_opens', 'date_started',
                    'date_last_drop', 'date_ended')


admin.site.register(Semester, SemesterAdmin)

### This chunk "appends" the fields of Person to those of User in the admin page
### https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#custom-permissions


# Define an inline admin descriptor for Person model
# which acts a bit like a singleton
class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False
    verbose_name_plural = 'person'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline, )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name', 'description')


admin.site.register(Department, DepartmentAdmin)


class MajorAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name', 'department_name')


admin.site.register(Major, MajorAdmin)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'credits_earned', 'grading_type')


admin.site.register(Course, CourseAdmin)


class SectionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'semester_name', 'professor_name', 'registered',
                    'waitlisted')


admin.site.register(Section, SectionAdmin)
