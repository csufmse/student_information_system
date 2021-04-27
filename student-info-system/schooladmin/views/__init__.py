from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Subquery
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html

from sis.authentication_helpers import role_login_required

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, Semester, Student,
                        SectionStudent, Profile, Message)

from sis.utils import filtered_table, filtered_table2, DUMMY_ID, next_prev

from sis.elements.course import (CoursesTable, CoursesForMajorTable, MajorCoursesMetTable,
                                 CourseCreationForm, CourseEditForm, CourseFilter)
from sis.elements.major import MajorCreationForm, MajorEditForm
from sis.elements.referenceitem import (ItemFilter, ProfReferenceItemsTable,
                                        ReferenceItemCreationForm)
from sis.elements.section import (SectionForClassTable, SectionsTable, SectionFilter,
                                  SectionCreationForm, SectionEditForm)
from sis.elements.sectionreferenceitem import SectionItemFilter, ReferenceItemsForSectionTable
from sis.elements.sectionstudent import (StudentHistoryTable, StudentInSectionTable,
                                         SectionStudentFilter)
from sis.elements.semester import (SemestersSummaryTable, SemestersTable, SemesterCreationForm,
                                   SemesterEditForm, SemesterFilter)
from sis.elements.user import (UsersTable, FullUsersTable, StudentsTable, StudentInMajorTable,
                               ProfessorsTable, StudentFilter, UserFilter, ProfessorFilter)

from easy_pdf import rendering

import schooladmin.views.users
from professor.views import sections as profsections
from student.views import current_schedule_view


def index(request):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role

    if not logged_in:
        return professors(request)
    if user_role == Profile.ACCESS_ADMIN:
        return schooladmin.views.users.userslist(request)
    elif user_role == Profile.ACCESS_PROFESSOR:
        return profsections(request)
    else:
        return current_schedule_view(request)


@role_login_required(Profile.ACCESS_ADMIN, Profile.ACCESS_PROFESSOR)
def students(request):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role
    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN

    qs = User.objects.all().filter(profile__role=Profile.ACCESS_STUDENT)
    if request.method == 'POST':
        if request.POST.get('attending-current') is not None:
            qs = qs.filter(profile__student__semesters__date_started__lte=datetime.now().date(),
                           profile__student__semesters__date_ended__gte=datetime.now().date())
        if request.POST.get('attending-upcoming') is not None:
            qs = qs.filter(
                profile__student__semesters__date_registration_opens__lte=datetime.now().date(),
                profile__student__semesters__date_registration_closes__gte=datetime.now().date())

    data = {
        'can_add': is_admin,
    }
    data.update(
        filtered_table2(
            name='students',
            qs=qs,
            filter=StudentFilter,
            table=StudentsTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:students'),
            click_url=reverse('schooladmin:student', args=[DUMMY_ID]),
        ))
    return render(request, 'schooladmin/students.html', data)


def professors(request):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role
    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN

    data = {
        'can_add': is_admin,
    }
    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}

    now = datetime.now().date()
    qs = User.objects.all().filter(profile__role=Profile.ACCESS_PROFESSOR)
    if request.method == 'POST':
        if request.POST.get('teaching-current') is not None:
            qs = qs.filter(profile__professor__id__in=Subquery(
                Section.objects.filter(semester__date_started__lte=now,
                                       semester__date_ended__gte=now).values('professor__id')))
            the_sem_qs = Semester.objects.filter(date_started__lte=now, date_ended__gte=now)
            if the_sem_qs.count() < 1:
                messages.error(request, f'No current semester.')
            else:
                messages.info(request,
                              f'{qs.count()} professors teaching in ' + f'{the_sem_qs[0].name}')

        if request.POST.get('teaching-upcoming') is not None:
            qs = qs.filter(profile__professor__id__in=Subquery(
                Section.objects.filter(semester__date_registration_opens__lte=now,
                                       semester__date_registration_closes__gte=now).values(
                                           'professor__id')))
            the_sem_qs = Semester.objects.filter(date_registration_opens__lte=now,
                                                 date_registration_closes__gte=now)
            if the_sem_qs.count() < 1:
                messages.error(request, f'No semester open for registration.')
            else:
                messages.info(request,
                              f'{qs.count()} professors teaching in ' + f'{the_sem_qs[0].name}')

    data.update(
        filtered_table2(
            name='professors',
            qs=qs,
            filter=ProfessorFilter,
            table=ProfessorsTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:professors'),
            click_url=reverse('schooladmin:professor', args=[DUMMY_ID]),
        ))

    return render(request, 'schooladmin/professors.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def professor_items(request, userid):
    logged_in = request.user.is_authenticated
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()

    if the_user.profile.role != Profile.ACCESS_PROFESSOR:
        return users.user(request, userid)

    data = {
        'auser': the_user,
    }
    data.update(
        filtered_table2(
            name='items',
            qs=the_user.profile.professor.referenceitem_set,
            filter=ItemFilter,
            table=ProfReferenceItemsTable,
            request=request,
            self_url=reverse('schooladmin:professor_items', args=[userid]),
            click_url=reverse('schooladmin:professor_item', args=[userid, DUMMY_ID]),
        ))

    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}
    return render(request, 'schooladmin/professor_items.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def professor_item(request, userid, item_id):
    return HttpResponse("not yet")


@role_login_required(Profile.ACCESS_ADMIN)
def professor_item_new(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_prof = qs[0]

    if the_prof.profile.role != Profile.ACCESS_PROFESSOR:
        messages.error(request, "That's not a professor.")
        return users.user(request, userid)

    if request.method == 'POST':
        form = ReferenceItemCreationForm(request.POST)
        if form.is_valid():
            the_new_item = form.save(commit=False)
            the_new_item.professor = the_prof.profile.professor
            the_new_item.save()
            form.save_m2m()
            messages.success(
                request, f'New item created for ' + f'{the_new_item.course} has been created.')
            return redirect('schooladmin:professor_items', userid=the_prof.id)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        dict = {}
        profs = Professor.objects.filter(profile__user_id=the_prof.id)
        dict['professor'] = profs[0]
        form = ReferenceItemCreationForm(initial=dict)
    return render(request, 'schooladmin/professor_new_item.html', {
        'form': form,
        'auser': the_prof
    })


# MAJORS


@role_login_required(Profile.ACCESS_ADMIN)
def major_edit(request, majorid):
    qs = Major.objects.filter(id=majorid)
    if qs.count() < 1:
        return HttpResponse("No such major")
    the_major = qs.get()

    if request.method == 'POST':
        form = MajorEditForm(request.POST, instance=the_major)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            form.save_m2m()
            messages.success(
                request, f'Major {the_major.abbreviation } / {the_major.name} has been updated.')
            return redirect('sis:major', the_major.id)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = MajorEditForm(instance=the_major)
    return render(request, 'schooladmin/major_edit.html', {'major': the_major, 'form': form})


@role_login_required(Profile.ACCESS_ADMIN)
def major_new_course(request, majorid):
    qs = Major.objects.filter(id=majorid)
    if qs.count() < 1:
        return HttpResponse("No such major")
    the_major = qs.get()
    return course_new(request, major=the_major)


@role_login_required(Profile.ACCESS_ADMIN)
def major_new(request):
    if request.method == 'POST':
        form = MajorCreationForm(request.POST)
        if form.is_valid():
            the_new_major = form.save()
            message = format_html('Major <a href="{}">{} / {}</a> has been created.',
                                  reverse('sis:major', args=[the_new_major.id]),
                                  the_new_major.abbreviation, the_new_major.title)
            messages.success(request, message)
            return redirect('sis:majors')
    else:
        form = MajorCreationForm()
    return render(request, 'schooladmin/major_new.html', {'form': form})


def courses(request):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role
    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN

    now = datetime.now().date()
    qs = Course.objects.all()
    if request.method == 'POST':
        if request.POST.get('offered-current') is not None:
            qs = qs.filter(id__in=Subquery(
                Section.objects.filter(semester__date_started__lte=now,
                                       semester__date_ended__gte=now).values('course__id')))
            the_sem_qs = Semester.objects.filter(date_started__lte=now, date_ended__gte=now)
            if the_sem_qs.count() < 1:
                messages.error(request, f'No current semester.')
            else:
                messages.info(request,
                              f'{qs.count()} courses offered in ' + f'{the_sem_qs[0].name}')

        if request.POST.get('offered-upcoming') is not None:
            qs = qs.filter(id__in=Subquery(
                Section.objects.filter(semester__date_registration_opens__lte=now,
                                       semester__date_registration_closes__gte=now).values(
                                           'course__id')))
            the_sem_qs = Semester.objects.filter(date_registration_opens__lte=now,
                                                 date_registration_closes__gte=now)
            if the_sem_qs.count() < 1:
                messages.error(request, f'No semester open for registration.')
            else:
                messages.info(request,
                              f'{qs.count()} courses offered in ' + f'{the_sem_qs[0].name}')

    data = {
        'can_add': is_admin,
    }
    data.update(
        filtered_table2(
            name='courses',
            qs=qs,
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:courses'),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))

    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}
    return render(request, 'schooladmin/courses.html', data)


def course(request, courseid):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role
    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN

    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()

    data = {'course': the_course, 'can_edit': is_admin}
    data.update(next_prev(request, 'courses', courseid))
    data.update(
        filtered_table2(
            name='sections',
            qs=Section.objects.filter(course=the_course),
            filter=SectionFilter,
            table=SectionForClassTable,
            request=request,
            self_url=reverse('schooladmin:course', args=[courseid]),
            click_url=reverse('schooladmin:section', args=[DUMMY_ID]),
        ))
    data.update(
        filtered_table2(
            name='prereqs',
            qs=Course.objects.filter(a_prerequisite__course=the_course),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            page_size=5,
            self_url=reverse('schooladmin:course', args=[courseid]),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))
    data.update(
        filtered_table2(
            name='neededby',
            qs=Course.objects.filter(a_course__prerequisite=the_course),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            page_size=10,
            self_url=reverse('schooladmin:course', args=[courseid]),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))

    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}
    return render(request, 'schooladmin/course.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def course_edit(request, courseid):
    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()

    if request.method == 'POST':
        form = CourseEditForm(request.POST, instance=the_course)
        if form.is_valid():
            updated_course = form.save()
            messages.success(request, f'Course {updated_course} successfully updated.')
            return redirect('schooladmin:course', courseid)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = CourseEditForm(instance=the_course)
    return render(request, 'schooladmin/course_edit.html', {'form': form, 'course': the_course})


@role_login_required(Profile.ACCESS_ADMIN)
def course_new(request, major=None):
    if request.method == 'POST':
        form = CourseCreationForm(request.POST)
        if form.is_valid():
            the_new_course = form.save()
            messages.success(request, f'Course {the_new_course} has been created.')
            return redirect('schooladmin:courses')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    elif major is not None:
        form = CourseCreationForm(initial={'major': major})
    else:
        form = CourseCreationForm()
    return render(request, 'schooladmin/course_new.html', {'form': form})


@role_login_required(Profile.ACCESS_ADMIN)
def course_section_new(request, courseid):
    return section_new_helper(request, courseid=courseid)


def semesters(request):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role
    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN

    data = {'can_add': is_admin}

    qs = Semester.objects.all()
    if request.method == 'POST':
        if request.POST.get('active') is not None:
            qs = Semester.active_semesters()
        elif request.POST.get('upcoming') is not None:
            qs = Semester.objects.filter(date_started__gte=datetime.now().date())

    data.update(
        filtered_table2(
            name='semesters',
            qs=qs,
            filter=SemesterFilter,
            table=SemestersTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:semesters'),
            click_url=reverse('schooladmin:semester', args=[DUMMY_ID]),
        ))
    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}
    return render(request, 'schooladmin/semesters.html', data)


def semester(request, semester_id):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role
    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN

    qs = Semester.objects.filter(id=semester_id)
    if qs.count() < 1:
        return HttpResponse("No such semester")
    the_semester = qs.get()

    data = {'semester': the_semester, 'can_add': is_admin}
    data.update(next_prev(request, 'semesters', semester_id))
    data.update(
        filtered_table2(
            name='sections',
            qs=Section.objects.filter(semester=the_semester),
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
            self_url=reverse('schooladmin:semester', args=[semester_id]),
            click_url=reverse('schooladmin:section', args=[DUMMY_ID]),
        ))
    if logged_in and user_role in (Profile.ACCESS_ADMIN, Profile.ACCESS_PROFESSOR):
        data.update(
            filtered_table2(
                name='students',
                qs=the_semester.students_attending(),
                filter=StudentFilter,
                table=StudentsTable,
                request=request,
                self_url=reverse('schooladmin:semester', args=[semester_id]),
                click_url=reverse('schooladmin:student', args=[DUMMY_ID]),
            ))
    data.update(
        filtered_table2(
            name='professors',
            qs=the_semester.professors_teaching(),
            filter=UserFilter,
            table=UsersTable,
            request=request,
            self_url=reverse('schooladmin:semester', args=[semester_id]),
            click_url=reverse('schooladmin:professor', args=[DUMMY_ID]),
        ))

    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}
    return render(request, 'schooladmin/semester.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def semester_edit(request, semester_id):
    qs = Semester.objects.filter(id=semester_id)
    if qs.count() < 1:
        return HttpResponse("No such semester")
    the_semester = qs.get()

    if request.method == 'POST':
        form = SemesterEditForm(request.POST, instance=the_semester)
        if form.is_valid():
            the_updated_sem = form.save()
            messages.success(request, f'Semester {the_updated_sem} has been updated.')
            return redirect('schooladmin:semester', semester_id)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = SemesterEditForm(instance=the_semester)
    return render(request, 'schooladmin/semester_edit.html', {
        'form': form,
        'semester': the_semester
    })


@role_login_required(Profile.ACCESS_ADMIN)
def semester_new(request):
    if request.method == 'POST':
        form = SemesterCreationForm(request.POST)
        if form.is_valid():
            try:
                the_new_semester = form.save()
                messages.success(request, f'Semester {the_new_semester} has been created.')
                return redirect('schooladmin:semesters')
            except Exception:
                messages.error(request,
                               'Semester is a duplicate of an existing one. Please correct.')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = SemesterCreationForm(initial={
            'year': date.today().year,
        })
    return render(request, 'schooladmin/semester_new.html', {'form': form})


@role_login_required(Profile.ACCESS_ADMIN)
def semester_section_new(request, semester_id):
    return section_new_helper(request, semester_id=semester_id)


def sections(request):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role
    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN

    data = {
        'can_add': is_admin,
    }
    data.update(
        filtered_table2(
            name='sections',
            qs=Section.objects.all(),
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:sections'),
            click_url=reverse('schooladmin:section', args=[DUMMY_ID]),
        ))
    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}
    return render(request, 'schooladmin/sections.html', data)


def section(request, sectionid):
    logged_in = request.user.is_authenticated
    if logged_in:
        the_profile = request.user.profile
        user_role = the_profile.role

    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN
    is_prof = logged_in and user_role == Profile.ACCESS_PROFESSOR
    can_see_students = logged_in and user_role in (Profile.ACCESS_ADMIN, Profile.ACCESS_PROFESSOR)

    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    data = {
        'section': the_section,
        'can_edit': is_admin,
        'can_refresh_items': is_prof and the_section.professor == the_profile.professor,
        'can_see_students': can_see_students,
    }
    data.update(next_prev(request, 'sections', sectionid))
    if can_see_students:
        data.update(
            filtered_table2(
                name='secstuds',
                qs=SectionStudent.objects.filter(section=the_section),
                filter=SectionStudentFilter,
                table=StudentInSectionTable,
                request=request,
                self_url=reverse('schooladmin:section', args=[sectionid]),
                click_url=reverse('schooladmin:sectionstudent', args=[DUMMY_ID]),
            ))
    data.update(
        filtered_table2(
            name='secitems',
            qs=the_section.sectionreferenceitem_set,
            filter=SectionItemFilter,
            table=ReferenceItemsForSectionTable,
            request=request,
            self_url=reverse('schooladmin:section', args=[sectionid]),
            click_url=reverse('sis:secitem', args=[DUMMY_ID]),
        ))

    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}
    return render(request, 'schooladmin/section.html', data)


@role_login_required(Profile.ACCESS_ADMIN, Profile.ACCESS_PROFESSOR)
def section_refreshitems(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    the_section.refresh_reference_items()

    messages.success(request, "Items refreshed for section")
    return redirect('schooladmin:section', sectionid)


@role_login_required(Profile.ACCESS_ADMIN)
def section_students_manage(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    return HttpResponse('not implemented yet')


@role_login_required(Profile.ACCESS_ADMIN)
def section_edit(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    if request.method == 'POST':
        form = SectionEditForm(request.POST, instance=the_section)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            form.save_m2m()
            obj.refresh_reference_items()
            messages.success(request, f'Section {obj} has been updated.')
            return redirect('schooladmin:section', sectionid)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = SectionEditForm(instance=the_section)
    return render(request, 'schooladmin/section_edit.html', {
        'form': form,
        'section': the_section
    })


@role_login_required(Profile.ACCESS_ADMIN)
def section_new_from_section(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()
    return section_new_helper(request,
                              courseid=the_section.course.id,
                              semester_id=the_section.semester.id)


@role_login_required(Profile.ACCESS_ADMIN)
def section_new(request):
    return section_new_helper(request)


def section_new_helper(request, semester_id=None, courseid=None):
    if request.method == 'POST':
        form = SectionCreationForm(request.POST)
        if form.is_valid():
            the_course = form.cleaned_data['course']
            the_sem = form.cleaned_data['semester']
            current_max_section = the_course.max_section_for_semester(the_sem)
            if current_max_section is None:
                next_section = 1
            else:
                next_section = current_max_section + 1
            the_new_section = form.save(commit=False)
            the_new_section.number = next_section
            the_new_section.save()
            the_new_section.refresh_reference_items()
            messages.success(request, f'Section {the_new_section} has been created.')
            return redirect('schooladmin:section', the_new_section.id)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form_values = {}
        if courseid is not None:
            qs = Course.objects.filter(id=courseid)
            if qs.count() < 1:
                return HttpResponse("No such course")
            the_course = qs.get()

            form_values['course'] = the_course

        if semester_id is not None:
            qs = Semester.objects.filter(id=semester_id)
            if qs.count() < 1:
                return HttpResponse("No such semester")
            the_semester = qs.get()
            form_values['semester'] = the_semester
        else:
            semesters = Semester.objects.order_by('-date_registration_opens').filter(
                date_registration_opens__lte=date.today(), date_last_drop__gte=date.today())
            if semesters.count() > 0:
                form_values['semester'] = semesters[0]

        form = SectionCreationForm(initial=form_values)
    return render(
        request, 'schooladmin/section_new.html', {
            'profs': Professor.objects.filter(profile__user__is_active=True),
            'courses': Course.objects.all(),
            'form': form,
        })


@login_required
def sectionstudent(request, id):
    qs = SectionStudent.objects.filter(id=id)
    if qs.count() < 1:
        return HttpResponse("No such sectionstudent")
    the_sectionstud = qs[0]
    is_admin = request.user.profile.role == Profile.ACCESS_ADMIN
    is_prof = request.user.profile.role == Profile.ACCESS_PROFESSOR

    if not is_admin and not is_prof and request.user.id != \
            the_sectionstud.student.profile.user.id:
        messages.error(request, "Something went wrong")
        return HttpResponse("Unauthorized")

    if the_sectionstud.status == SectionStudent.GRADED:
        grade = the_sectionstud.letter_grade
    else:
        grade = '(N/A)'

    data = {
        'secstud': the_sectionstud,
        'student': the_sectionstud.student,
        'section': the_sectionstud.section,
        'grade': grade
    }
    return render(request, 'schooladmin/sectionstudent.html', data)


@role_login_required(Profile.ACCESS_ADMIN, Profile.ACCESS_PROFESSOR)
def transcript(request, userid):
    # prepare the data
    student = Student.objects.get(profile__user__id=userid)
    semesters = []
    ssects = student.sectionstudent_set.all().order_by('section__semester',
                                                       'section__course__name')
    last_sem = {
        'semester': None,
    }
    for ssect in ssects:
        if ssect.section.semester != last_sem['semester']:
            if last_sem['semester'] is not None:
                semesters.append(last_sem)
            last_sem = {
                'semester': ssect.section.semester,
                'gpa': student.gpa(semester=ssect.section.semester),
                'sections': [],
                'credits_earned': student.credits_earned(semester=ssect.section.semester),
            }
        last_sem['sections'].append(ssect)

    data = {
        'student': student,
        'date_prepared': datetime.now().date(),
        'semesters': semesters,
    }

    filename = f'{student.profile.name}-{datetime.now().strftime("%Y%m%d-%H%M")}'.replace(
        ' ', '_')

    # FOR TESTING -- render as HTML
    # return render(request,'schooladmin/transcript.html',data)

    # generate the PDF
    return rendering.render_to_pdf_response(request,
                                            'schooladmin/transcript.html',
                                            data,
                                            filename=filename,
                                            content_type='application/pdf',
                                            response_class=HttpResponse)


@role_login_required(Profile.ACCESS_ADMIN, Profile.ACCESS_PROFESSOR)
def demographics(request):
    logged_in = request.user.is_authenticated
    students = Profile.demographics_for(Profile.objects.filter(role=Profile.ACCESS_STUDENT))
    professors = Profile.demographics_for(Profile.objects.filter(role=Profile.ACCESS_PROFESSOR))

    # FORMAT RESULTS
    stud_form = [{'key': 'Total Students', 'data': '', 'total': students['count']}]
    del students['count']
    for attr in Profile.DEMO_ATTRIBUTE_MAP:
        attrdata = students[attr[2]]
        total = 0
        line = ''
        for item in attrdata.items():
            line += f', {item[0]} = {item[1]}'
            total += item[1]
        line = line[2:]
        stud_form.append({'key': attr[2], 'data': line, 'total': total})

    prof_form = [{'key': 'Total Professors', 'data': '', 'total': professors['count']}]
    del professors['count']
    for attr in Profile.DEMO_ATTRIBUTE_MAP:
        attrdata = professors[attr[2]]
        total = 0
        line = ''
        for item in attrdata.items():
            line += f', {item[0]} = {item[1]}'
            total += item[1]
        line = line[2:]
        prof_form.append({'key': attr[2], 'data': line, 'total': total})

    data = {
        'students': stud_form,
        'professors': prof_form,
        'date_prepared': datetime.now().date(),
    }

    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}
    return render(request, 'schooladmin/demographics.html', data)
