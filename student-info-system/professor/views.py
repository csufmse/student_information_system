from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from django_tables2 import RequestConfig

from sis.authentication_helpers import role_login_required
from sis.models import (Course, Professor, Section, Semester, Student, Profile, SectionStudent,
                        ReferenceItem, SectionReferenceItem)
from sis.tables.sections import ProfSectionsTable
from sis.utils import filtered_table2, DUMMY_ID
from sis.filters.section import SectionFilter

from professor.forms import ReferenceItemForm


@role_login_required(Profile.ACCESS_PROFESSOR)
def index(request):
    return render(request, 'professor/home_professor.html',
                  request.user.profile.unread_messages())


@role_login_required(Profile.ACCESS_PROFESSOR)
def sections(request):
    the_prof = request.user.profile.professor
    sections_qs = Section.objects.filter(professor=the_prof)
    sections = {}
    # set up our sectons qs dictionary by semester
    for sect in sections_qs:
        if sect.semester.name not in sections.keys():
            sections[sect.semester.name] = [sect.semester.id]

    # fill in our sections dictionary with tables by semester
    for name, sem in sections.items():
        qs = sections_qs.filter(semester=sem[0])
        table = ProfSectionsTable(qs)
        RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
        sections[name].append(table)

    if request.method == 'POST':
        sem = request.POST.get('semester')
        table = sections[sem][1]
    else:
        sem = Semester.current_semester().name
        values = sections.get(sem)
        if values is not None:
            table = values[1]
    print(table)
    return render(request, 'professor/sections.html', {
        'table': table,
        'semesters': sections.keys()
    })


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
    data = {'sectionid': sectionid}

    if request.method == 'POST':
        form = ReferenceItemForm(request.POST)
        data['form'] = form

        if form.is_valid():
            new_ref = form.save(commit=False)
            new_ref.professor = request.user.profile.professor
            section = Section.objects.get(id=sectionid)
            course = Course.objects.get(id=section.course.id)
            new_ref.course = course

            try:
                new_ref.save()
            except IntegrityError as e:
                if 'UNIQUE constraint' in e.args[0]:
                    messages.error(request, "That Reference Item already exists.")
                else:
                    messages.error(request,
                                   "There was a problem saving the new item to the database.")
                return render(request, 'professor/reference_add.html', data)

            # Specify all current and future sections by reg date or only current sections by reg date
            if request.POST.get('semester_future') == 'future':
                sects_to_update = course.section_set.exclude(
                    status__in=[Section.REG_CLOSED, Section.CANCELLED])
            else:
                sects_to_update = course.section_set.filter(semester=section.semester)

            for sect in sects_to_update:
                sect.refresh_reference_items()
            messages.success(request, "New reference item successfully created")
            return redirect('professor:section', sectionid)

        else:
            messages.error(request, "Please correct the error(s) below")
            return render(request, 'professor/reference_add.html', data)
    else:
        form = ReferenceItemForm()

    data['form'] = form
    return render(request, 'professor/reference_add.html', data)
