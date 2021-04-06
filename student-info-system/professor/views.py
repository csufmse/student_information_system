from django.http import HttpResponse
from django.shortcuts import render
from django_tables2 import RequestConfig

from sis.authentication_helpers import role_login_required
from sis.models import Professor, Section, AccessRoles, Semester, SectionStudent
from sis.utils import filtered_table

from schooladmin.tables import SectionsTable, StudentInSectionTable
from schooladmin.filters import StudentFilter

from .tables import StudentsTable


@role_login_required(AccessRoles.PROFESSOR_ROLE)
def index(request):
    return render(request, 'professor/home_professor.html')


@role_login_required(AccessRoles.PROFESSOR_ROLE)
def sections(request):
    the_prof = request.user.professor

    if the_prof is None:
        return HttpResponse("No such professor")

    sections_qs = Section.objects.filter(professor=the_prof).exclude(status=Section.CLOSED)
    sections_table = SectionsTable(sections_qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(sections_table)

    return render(request, 'professor/sections.html', {'sections': sections_table})


@role_login_required(AccessRoles.PROFESSOR_ROLE)
def students_in_section(request, sectionid):
    data = {}
    section = Section.objects.get(id=sectionid)
    ssects = SectionStudent.objects.filter(section=section)
    if request.method == "POST":
        for student in section.students.all():
            if request.POST.get(str(student)):
                ssect = ssects.get(student=student)
                ssect.grade = request.POST.get(str(student))
                ssect.save()
                data['grade_submitted'] = {True}

    data.update({'grades': SectionStudent.GRADES, 'section': section, 'ssects': ssects})
    return render(request, 'professor/students.html', data)
