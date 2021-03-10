from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Person, Semester, Major, Course, Section


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_registration_opens', 'date_started',
                    'date_last_drop', 'date_ended')


admin.site.register(Semester, SemesterAdmin)

# This chunk "appends" the fields of Person to those of User in the admin page
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#custom-permissions


# Define an inline admin descriptor for Person model
# which acts a bit like a singleton
class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False
    verbose_name_plural = 'people'
    fk_name = 'user'


# Define a new User admin
class CustomUserAdmin(UserAdmin):
    inlines = (PersonInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class MajorAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name')


admin.site.register(Major, MajorAdmin)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'credits_earned', 'grading_type')


admin.site.register(Course, CourseAdmin)


class SectionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'semester_name', 'professor_name', 'registered',
                    'waitlisted')


admin.site.register(Section, SectionAdmin)
