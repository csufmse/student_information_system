from django.http import HttpResponse
from django.shortcuts import render
from django_tables2 import RequestConfig

from sis.authentication_helpers import role_login_required
from sis.models import Professor, Section, AccessRoles, Semester
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
    if request.POST:
        request.POST.get
    data = {'section': Section.objects.get(id=sectionid)}
    data.update(
        filtered_table(name='students',
                       qs=Section.objects.get(id=sectionid).students.all(),
                       filter=StudentFilter,
                       table=StudentsTable,
                       request=request))
    return render(request, 'professor/students.html', data)
