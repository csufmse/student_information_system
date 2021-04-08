from django.http import HttpResponse
from django.shortcuts import render
from django_tables2 import RequestConfig

from sis.authentication_helpers import role_login_required
from sis.models import Professor, Section, Semester, Student, Profile, SectionStudent
from sis.utils import filtered_table

from schooladmin.tables import SectionsTable, StudentInSectionTable
from schooladmin.filters import StudentFilter

from .tables import StudentsTable


@role_login_required(Profile.ACCESS_PROFESSOR)
def index(request):
    return render(request, 'professor/home_professor.html')


@role_login_required(Profile.ACCESS_PROFESSOR)
def sections(request):
    the_prof = request.user.profile.professor

    if the_prof is None:
        return HttpResponse("No such professor")

    sections_qs = Section.objects.filter(professor=the_prof).exclude(status=Section.CLOSED)
    sections_table = SectionsTable(sections_qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(sections_table)

    return render(request, 'professor/sections.html', {'sections': sections_table})


@role_login_required(Profile.ACCESS_PROFESSOR)
def students_in_section(request, sectionid):
    data = {}
    section = Section.objects.get(id=sectionid)
    ssects = SectionStudent.objects.filter(section=section)
    if request.method == "POST":
        for student in section.students.all():
            if request.POST.get(str(student.pk)) != 'None':
                ssect = ssects.get(student=student)
                ssect.grade = request.POST.get(str(student.pk))
                ssect.save()
                data['grade_submitted'] = {True}
    grades = ((None, None), ('A', 4), ('B', 3), ('C', 2), ('D', 1), ('F', 1))
    data.update({'grades': grades, 'section': section, 'ssects': ssects})
    return render(request, 'professor/students.html', data)


@role_login_required(Profile.ACCESS_PROFESSOR)
def student(request, studentid):
    stud = Student.objects.get(pk=studentid)
    ssects = stud.sectionstudent_set.all()
    data = {'student': stud, 'ssects': ssects}
    return render(request, 'professor/student.html', data)
