from django.http import HttpResponse
from django.shortcuts import render
from django_tables2 import RequestConfig

from sis.authentication_helpers import role_login_required
from sis.models import Professor, Section, AccessRoles, Semester

from .tables import SectionsTable


@role_login_required(AccessRoles.PROFESSOR_ROLE)
def index(request):
    return render(request, 'home_professor.html')


@role_login_required(AccessRoles.PROFESSOR_ROLE)
def sections(request):
    the_prof = request.user.professor

    if the_prof is None:
        return HttpResponse("No such professor")

    sections_qs = Section.objects.filter(professor=the_prof).exclude(status=Section.CLOSED)
    sections_table = SectionsTable(sections_qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(sections_table)

    return render(request, 'sections.html', {'sections': sections_table})
