from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Student, Professor, Major, TranscriptRequest, Course, Semester, Section, SectionStudent, CoursePrerequisite


class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'major', 'gpa', 'class_level')


admin.site.register(Student, StudentAdmin)


class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'major')


admin.site.register(Professor, ProfessorAdmin)


class MajorAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name', 'description')


admin.site.register(Major, MajorAdmin)


class TranscriptRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'date_requested', 'date_fulfilled')


admin.site.register(TranscriptRequest, TranscriptRequestAdmin)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('major', 'name', 'title', 'description', 'credits_earned')


admin.site.register(Course, CourseAdmin)


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_registration_opens', 'date_started',
                    'date_last_drop', 'date_ended')


admin.site.register(Semester, SemesterAdmin)


class SectionAdmin(admin.ModelAdmin):
    list_display = ('semester', 'name', 'professor', 'registered', 'capacity')


admin.site.register(Section, SectionAdmin)


class SectionStudentAdmin(admin.ModelAdmin):
    list_display = ('section', 'student', 'status', 'grade', 'professor')


admin.site.register(SectionStudent, SectionStudentAdmin)


class CoursePrerequisiteAdmin(admin.ModelAdmin):
    list_display = ('course', 'prerequisite')


admin.site.register(CoursePrerequisite, CoursePrerequisiteAdmin)
