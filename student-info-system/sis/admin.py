from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                     Semester, SemesterStudent, Student, Profile)

admin.site.site_title = "CSUF Student Information System Site Admin"
admin.site.site_header = "Administrative Access to ALL Data"
admin.site.index_title = "Database Access"


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'bio')


admin.site.register(Profile, ProfileAdmin)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'major')


admin.site.register(Student, StudentAdmin)


class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'major')


admin.site.register(Professor, ProfessorAdmin)


class MajorAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name', 'description')


admin.site.register(Major, MajorAdmin)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('major', 'name', 'title', 'description', 'credits_earned')


admin.site.register(Course, CourseAdmin)


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_registration_opens', 'date_registration_closes', 'date_started',
                    'date_last_drop', 'date_ended')


admin.site.register(Semester, SemesterAdmin)


class SectionAdmin(admin.ModelAdmin):
    list_display = ('semester', 'name', 'professor', 'hours', 'location', 'registered',
                    'capacity')


admin.site.register(Section, SectionAdmin)


class SectionStudentAdmin(admin.ModelAdmin):
    list_display = ('section', 'student', 'status', 'grade', 'professor')


admin.site.register(SectionStudent, SectionStudentAdmin)


class SemesterStudentAdmin(admin.ModelAdmin):
    list_display = ('semester', 'student')


admin.site.register(SemesterStudent, SemesterStudentAdmin)


class CoursePrerequisiteAdmin(admin.ModelAdmin):
    list_display = ('course', 'prerequisite')


admin.site.register(CoursePrerequisite, CoursePrerequisiteAdmin)
