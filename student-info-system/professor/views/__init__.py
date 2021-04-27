from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, redirect

from django_tables2 import RequestConfig

from sis.authentication_helpers import role_login_required

from sis.elements.section import ProfSectionsTable, SectionFilter
from sis.elements.referenceitem import ReferenceItemForm
from sis.models import (Course, Professor, Section, Semester, Student, Profile, SectionStudent,
                        ReferenceItem, SectionReferenceItem)


@role_login_required(Profile.ACCESS_PROFESSOR)
def index(request):
    data = {
        'current_semester': Semester.current_semester(),
        'registration_open': Semester.semesters_open_for_registration(),
    }
    data.update(request.user.profile.unread_messages())
    return render(request, 'professor/home_professor.html', data)


@role_login_required(Profile.ACCESS_PROFESSOR)
def sections(request):
    the_prof = request.user.profile.professor
    sections_qs = Section.objects.filter(professor=the_prof)
    sections = {}
    # set up our sections qs dictionary by semester
    for sect in sections_qs:
        if sect.semester.finalized():
            continue
        if sect.semester.name not in sections.keys():
            sections[sect.semester.name] = [sect.semester.id]

    # fill in our sections dictionary with tables by semester
    for name, sem in sections.items():
        qs = sections_qs.filter(semester=sem[0])
        table = ProfSectionsTable(qs)
        RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
        sections[name].append(table)

    data = {
        'semesters': sections.keys(),
    }
    if request.method == 'POST':
        sem = request.POST.get('semester')
        table = sections[sem][1]
        data['table'] = table
    else:
        sem = Semester.current_semester().name
        values = sections.get(sem)
        if values is not None:
            table = values[1]
            data['table'] = table
    return render(request, 'professor/sections.html', data)


@role_login_required(Profile.ACCESS_PROFESSOR)
def section(request, sectionid):
    data = {}
    aSection = Section.objects.get(id=sectionid)
    references = aSection.sectionreferenceitem_set.all()
    ssects = SectionStudent.objects.filter(section=aSection)
    if request.method == "POST":
        for student in aSection.students.all():
            if request.POST.get(str(student.pk)) != 'No Change':
                ssect = ssects.get(student=student)
                grade_value = request.POST.get(str(student.pk))
                ssect.grade = grade_value if grade_value != 'No Grade Assigned' else None
                ssect.save()
                data['grade_submitted'] = {True}
    grades = (
        ('No Change', 'No Change'),
        ('No Grade Assigned', 'No Grade Assigned'),
    ) + SectionStudent.POINTS
    data.update({
        'grades': grades,
        'section': aSection,
        'ssects': ssects,
        'references': references,
        'can_grade': not aSection.semester.finalized(),
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

            # Specify all current+future sects by reg date or only current sections by reg date
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
