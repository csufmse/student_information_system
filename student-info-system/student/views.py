from datetime import date

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render

from schooladmin.filters import SectionFilter
from sis.authentication_helpers import role_login_required
from sis.models import (Course, Section, Profile, Semester, SectionStudent, SemesterStudent)
from sis.utils import filtered_table


@role_login_required(Profile.ACCESS_STUDENT)
def index(request):
    return render(request, 'student/home_student.html')


@role_login_required(Profile.ACCESS_STUDENT)
def current_schedule_view(request):
    context = {
        'my_sections': request.user.profile.student.sectionstudent_set.all,
        'name': request.user.profile.student.name
    }
    return render(request, 'student/current_schedule.html', context)


@role_login_required(Profile.ACCESS_STUDENT)
def registration_view(request):
    has_filter = None
    student = request.user.profile.student
    # If the student has to register for semesters first, do this:
    # semester_list = student.semesters.order_by('-date_started')
    # if semester_list.count() == 0:
    #     return HttpResponse("You are not registered for any semesters.")
    # If the student can register for anything open, do this:
    semester_list = Semester.objects.filter(
        date_registration_opens__lte=date.today(),
        date_registration_closes__gte=date.today()).order_by('-date_started')
    context = {'student': student, 'semesters': semester_list}

    if request.method == 'POST':
        qs = semester_list.filter(id=request.POST.get('semester'))
        if qs.count() == 1:
            the_sem = qs.get()
            context['semester'] = the_sem.id
            the_sections = the_sem.section_set.exclude(students=student)
            filt = SectionFilter(request.GET, queryset=the_sections)
            has_filter = any(field in request.GET for field in set(filt.get_fields()))
            context['sections'] = filt.qs
            context['any_sections'] = filt.qs.count() != 0

            if request.POST.get('register') is not None:
                any_selected = False

                for sect in filt.qs:
                    # indicate student is attending this semester...
                    sem = SemesterStudent.objects.filter(student=student, semester=sect.semester)
                    if sem.count() < 1:
                        SemesterStudent.objects.create(student=student, semester=sect.semester)

                    course_val = request.POST.get(str(sect.course.id))
                    if course_val is not None and int(course_val) == sect.id:
                        status = SectionStudent.REGISTERED
                        if sect.seats_remaining < 1:
                            status = SectionStudent.WAITLISTED
                        sectstud = SectionStudent(section=sect, student=student, status=status)
                        sectstud.save()
                        # any_selected = True
                        sect.is_selected = True
                        context['registration_success'] = True

            # did we complete a registration?
            # if any_selected:
            # return redirect('student:registration')

    else:
        the_sem = semester_list[0]
        context['semester'] = the_sem.id
        the_sections = the_sem.section_set.exclude(students=student)
        filt = SectionFilter(request.GET, queryset=the_sections)
        has_filter = any(field in request.GET for field in set(filt.get_fields()))
        context['sections'] = filt.qs
        context['any_sections'] = the_sections.count() != 0

    if has_filter is not None:
        context['has_filter'] = has_filter
        context['filter'] = filt
    # signal template that this entry is a different course from last section
    last_course = None
    for sect in context['sections']:
        sect.new_course = sect.course != last_course
        if sect.new_course:
            last_course = sect.course

    return render(request, 'student/registration.html', context)
