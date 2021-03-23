from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django_tables2 import RequestConfig
from sis.authentication_helpers import role_login_required
from .tables import (UsersTable, MajorsTable, BasicProfsTable, BasicCoursesTable, SemestersTable,
                     CoursesTable, SectionsTable, SectionStudentsTable)
from sis.models import (Student, Admin, Professor, Major, Course, CoursePrerequisite, Semester,
                        Section)


@role_login_required('Professor')
def index(request):
    return render(request, 'home_professor.html')


@role_login_required('Professor')
def courses(request):
    u = request.user

    qs = Professor.objects.filter(user__id=3)
    if qs.count() < 1:
        return HttpResponse("No such professor")
    the_prof = qs[0]

    sections_qs = Section.objects.filter(professor=the_prof)
    sections_table = SectionsTable(sections_qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(
        sections_table)

    return render(request, 'sections.html', {'sections': sections_table})
