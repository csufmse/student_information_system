from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_tables2 import RequestConfig

from sis.authentication_helpers import role_login_required
from sis.models import (Professor, Section, Semester, Student, Profile, SectionStudent,
                        ReferenceItem, SectionReferenceItem)
from sis.utils import filtered_table
from sis.tables.sections import ProfSectionsTable

from professor.forms import ReferenceItemForm


@role_login_required(Profile.ACCESS_PROFESSOR)
def index(request):
    return render(request, 'professor/home_professor.html',
                  request.user.profile.unread_messages())


@role_login_required(Profile.ACCESS_PROFESSOR)
def sections(request):
    the_prof = request.user.profile.professor
    sections_qs = Section.objects.filter(professor=the_prof).exclude(status=Section.REG_CLOSED)
    sections_table = ProfSectionsTable(sections_qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(sections_table)

    return render(request, 'professor/sections.html', {'sections': sections_table})


@role_login_required(Profile.ACCESS_PROFESSOR)
def section(request, sectionid):
    data = {}
    section = Section.objects.get(id=sectionid)
    references = section.sectionreferenceitem_set.all()
    ssects = SectionStudent.objects.filter(section=section)
    if request.method == "POST":
        for student in section.students.all():
            if request.POST.get(str(student.pk)) != 'None':
                ssect = ssects.get(student=student)
                ssect.grade = request.POST.get(str(student.pk))
                ssect.save()
                data['grade_submitted'] = {True}
    grades = ((None, None), ('A', 4), ('B', 3), ('C', 2), ('D', 1), ('F', 1))
    data.update({
        'grades': grades,
        'section': section,
        'ssects': ssects,
        'references': references
    })
    return render(request, 'professor/section.html', data)


@role_login_required(Profile.ACCESS_PROFESSOR)
def student(request, studentid):
    stud = Student.objects.get(pk=studentid)
    ssects = stud.sectionstudent_set.all()
    data = {'student': stud, 'ssects': ssects}
    return render(request, 'professor/student.html', data)


@role_login_required(Profile.ACCESS_PROFESSOR)
def add_reference(request, sectionid):
    if request.method == 'POST':
        form = ReferenceItemForm(request.POST)
        if form.is_valid():
            new_ref = form.save(commit=False)
            new_ref.professor = request.user.profile.professor
            section = Section.objects.get(id=sectionid)
            new_ref.course = section.course
            try:
                new_ref.save()
            except IntegrityError as e:
                if 'UNIQUE constraint' in e.args[0]:
                    messages.error(request, "That Reference Item already exists.")
                else:
                    messages.error(request,
                                   "There was a problem saving the new item to the database.")
                return redirect('professor:add_reference', sectionid)
            section.refresh_reference_items()
            messages.success(request, "New reference item successfully created")
            return redirect('professor:section', sectionid)
        else:
            messages.error(request, "Please correct the error(s) below")
            return redirect('professor:add_reference', sectionid)
    else:
        form = ReferenceItemForm()

    data = {'form': form, 'sectionid': sectionid}
    return render(request, 'professor/reference_add.html', data)
