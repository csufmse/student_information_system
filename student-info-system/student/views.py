from datetime import date

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render

from schooladmin.views import major as admin_major
from schooladmin.filters import (CourseFilter, SectionFilter, SectionStudentFilter,
                                 SemesterFilter, SentMessageFilter, ReceivedMessageFilter,
                                 StudentFilter)
from sis.authentication_helpers import role_login_required
from sis.models import (Course, Section, Profile, Semester, SectionStudent, SemesterStudent)
from sis.utils import filtered_table

from sis.tables.courses import CoursesTable, MajorCoursesMetTable
from sis.tables.messages import MessageSentTable, MessageReceivedTable
from sis.tables.sectionreferenceitems import SectionReferenceItemsTable
from sis.tables.sectionstudents import StudentHistoryTable
from sis.tables.semesters import SemestersSummaryTable

from sis.filters.sectionreferenceitem import SectionItemFilter

from sis.forms.profile import DemographicForm, UnprivProfileEditForm
from sis.forms.user import UserEditForm


@role_login_required(Profile.ACCESS_STUDENT)
def index(request):
    return render(request, 'student/home_student.html')


@role_login_required(Profile.ACCESS_STUDENT)
def current_schedule_view(request):
    current_semester = Semester.current_semester()
    context = {
        'my_sections':
            request.user.profile.student.sectionstudent_set.filter(
                section__semester=current_semester),
        'name':
            request.user.profile.student.name,
        'semester':
            current_semester,
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
        if len(semester_list) > 0:
            the_sem = semester_list[0]
            context['semester'] = the_sem.id
            the_sections = the_sem.section_set.exclude(students=student)
            filt = SectionFilter(request.GET, queryset=the_sections)
            has_filter = any(field in request.GET for field in set(filt.get_fields()))
            context['sections'] = filt.qs
            context['any_sections'] = the_sections.count() != 0
        else:
            context['any_sections'] = 0

    if has_filter is not None:
        context['has_filter'] = has_filter
        context['filter'] = filt
    # signal template that this entry is a different course from last section
    last_course = None
    if 'sections' in context:
        for sect in context['sections']:
            sect.new_course = sect.course != last_course
            if sect.new_course:
                last_course = sect.course

    return render(request, 'student/registration.html', context)


@role_login_required(Profile.ACCESS_STUDENT)
def profile(request):
    the_user = request.user

    data = {
        'user': the_user,
    }
    data.update(
        filtered_table(
            name='semesters',
            qs=the_user.profile.student.semesters.all(),
            filter=SemesterFilter,
            table=SemestersSummaryTable,
            request=request,
            wrap_list=False,
        ))

    data.update(
        filtered_table(
            name='history',
            qs=the_user.profile.student.course_history(),
            filter=SectionStudentFilter,
            table=StudentHistoryTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='remaining',
            qs=the_user.profile.student.remaining_required_courses(),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='majorcourses',
            qs=the_user.profile.student.requirements_met_list(),
            filter=CourseFilter,
            table=MajorCoursesMetTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='received',
            qs=the_user.profile.sent_to.filter(time_archived__isnull=True),
            filter=ReceivedMessageFilter,
            table=MessageReceivedTable,
            request=request,
            wrap_list=False,
        ))
    data.update(
        filtered_table(
            name='sent',
            qs=the_user.profile.sent_by.filter(time_archived__isnull=True),
            filter=SentMessageFilter,
            table=MessageSentTable,
            request=request,
            wrap_list=False,
        ))

    return render(request, 'student/student.html', data)


@transaction.atomic
@role_login_required(Profile.ACCESS_STUDENT)
def profile_edit(request):
    the_user = request.user
    user_profile = the_user.profile
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=the_user, prefix='u')
        profile_form = UnprivProfileEditForm(request.POST, instance=user_profile, prefix='p')
        demo_form = DemographicForm(request.POST, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid() and demo_form.is_valid():
            user_form.save()
            profile_form.save()
            demo_form.save()
            messages.success(request, "Profile has been updated.")
            return profile(request)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        user_form = UserEditForm(instance=the_user, prefix='u')
        profile_form = UnprivProfileEditForm(instance=user_profile, prefix='p')
        demo_form = DemographicForm(instance=user_profile,)

    return render(
        request, 'student/student_edit.html', {
            'user': the_user,
            'user_form': user_form,
            'profile_form': profile_form,
            'demo_form': demo_form,
        })


@role_login_required(Profile.ACCESS_STUDENT)
def major(request, majorid):
    return admin_major(request, majorid)


@role_login_required(Profile.ACCESS_STUDENT)
def change_password(request):
    return HttpResponse("student:change_password not implemented")


@role_login_required(Profile.ACCESS_STUDENT)
def course(request, courseid):
    return HttpResponse("student:course not implemented")


@role_login_required(Profile.ACCESS_STUDENT)
def sectionstudent(request, id):
    return HttpResponse("student:sectionstudent not implemented")


@role_login_required(Profile.ACCESS_STUDENT)
def semester(request, semester_id):
    return HttpResponse("student:semester not implemented")


@role_login_required(Profile.ACCESS_STUDENT)
def user(request, userid):
    return HttpResponse("student:user not implemented")


@role_login_required(Profile.ACCESS_STUDENT)
def secitem(request, id):
    return HttpResponse("student:secitem not implemented")


@role_login_required(Profile.ACCESS_STUDENT)
def section(request, sectionid):
    return HttpResponse("student:section not implemented")


@role_login_required(Profile.ACCESS_STUDENT)
def secitems(request):
    the_user = request.user
    the_semester = Semester.current_semester()
    data = {
        'user': the_user,
        'semester': the_semester,
    }
    data.update(
        filtered_table(
            name='secitem',
            qs=the_user.profile.student.section_reference_items_for(the_semester),
            filter=SectionItemFilter,
            table=SectionReferenceItemsTable,
            request=request,
        ))

    return render(request, 'student/items.html', data)
