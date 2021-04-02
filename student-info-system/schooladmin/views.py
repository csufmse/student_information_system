from datetime import date

from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django_tables2 import RequestConfig
from django.utils.html import format_html
from django.urls import reverse

from sis.authentication_helpers import role_login_required
from sis.models import (Admin, Course, CoursePrerequisite, Major, Professor, Section, Semester,
                        Student, SectionStudent, AccessRoles)

from .filters import (CourseFilter, MajorFilter, SectionFilter, SectionStudentFilter,
                      SemesterFilter, UserFilter)
from .forms import (CourseCreationForm, CourseEditForm, CustomUserCreationForm, MajorCreationForm,
                    MajorEditForm, SectionCreationForm, SectionEditForm, SemesterCreationForm,
                    UserEditForm, SemesterEditForm)
from .tables import (UsersTable, CoursesTable, MajorsTable, SectionsTable, SemestersTable,
                     FullUsersTable, StudentHistoryTable, StudentInMajorTable,
                     StudentInSectionTable, SemestersSummaryTable, SectionForClassTable,
                     CoursesForMajorTable)


# helper function to make tables
# merge the result of this into the response data
def filtered_table(name=None, qs=None, filter=None, table=None, request=None, page_size=25):
    filt = filter(request.GET, queryset=qs, prefix=name)
    # weird "{name}" thing is because the HTML field has the prefix but the Filter does
    # NOT have it in the field names
    has_filter = any(f'{name}-{field}' in request.GET for field in set(filt.get_fields()))
    tab = table(list(filt.qs))
    RequestConfig(request, paginate={"per_page": page_size, "page": 1}).configure(tab)
    return {name + '_table': tab, name + '_filter': filt, name + '_has_filter': has_filter}


@role_login_required(AccessRoles.ADMIN_ROLE)
def index(request):
    return render(request, 'schooladmin/home_admin.html')


# USERS


@role_login_required(AccessRoles.ADMIN_ROLE)
def users(request):
    return render(
        request, 'schooladmin/users.html',
        filtered_table(
            name='users',
            qs=User.annotated(),
            filter=UserFilter,
            table=FullUsersTable,
            request=request,
        ))


@role_login_required(AccessRoles.ADMIN_ROLE)
def user(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()
    if request.method == 'POST':
        if request.POST.get('disbutton'):
            the_user.is_active = False
            the_user.save()
            messages.success(request,
                             f'User {the_user.get_full_name()} has been disabled from login.')
        elif request.POST.get('enabutton'):
            the_user.is_active = True
            the_user.save()
            messages.success(request,
                             f'User {the_user.get_full_name()} has been enabled for login.')
        return redirect('schooladmin:users')

    if the_user.access_role() == AccessRoles.STUDENT_ROLE:
        return student(request, userid)
    elif the_user.access_role() == AccessRoles.PROFESSOR_ROLE:
        return professor(request, userid)

    formdata = {
        'user': the_user,
    }

    return render(request, 'schooladmin/user.html', formdata)


@role_login_required(AccessRoles.ADMIN_ROLE)
def student(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()

    if the_user.access_role() != AccessRoles.STUDENT_ROLE:
        return user(request, userid)

    if request.method == 'POST':
        if request.POST.get('disbutton'):
            the_user.is_active = False
            the_user.save()
        elif request.POST.get('enabutton'):
            the_user.is_active = True
            the_user.save()
        return redirect('schooladmin:users')

    data = {
        'user': the_user,
    }
    data.update(
        filtered_table(
            name='semesters',
            qs=the_user.student.semesters,
            filter=SemesterFilter,
            table=SemestersSummaryTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='history',
            qs=the_user.student.course_history(),
            filter=SectionStudentFilter,
            table=StudentHistoryTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='remaining',
            qs=the_user.student.remaining_required_courses(),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
        ))

    return render(request, 'schooladmin/student.html', data)


@role_login_required(AccessRoles.ADMIN_ROLE)
def professor(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()

    if the_user.access_role() != AccessRoles.PROFESSOR_ROLE:
        return user(request, userid)

    if request.method == 'POST':
        if request.POST.get('disbutton'):
            the_user.is_active = False
            the_user.save()
        elif request.POST.get('enabutton'):
            the_user.is_active = True
            the_user.save()
        return redirect('schooladmin:users')

    data = {
        'user': the_user,
    }
    data.update(
        filtered_table(
            name='semesters',
            qs=the_user.professor.semesters_teaching(),
            filter=SemesterFilter,
            table=SemestersSummaryTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='sections',
            qs=the_user.professor.section_set,
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
        ))

    return render(request, 'schooladmin/professor.html', data)


@role_login_required(AccessRoles.ADMIN_ROLE)
def user_change_password(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()
    if request.method == 'POST':
        form = AdminPasswordChangeForm(the_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Password for "{the_user.username}" {the_user.get_full_name()} ' +
                'was successfully updated.')
            return redirect('schooladmin:user', userid)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = AdminPasswordChangeForm(request.user)
    return render(request, 'schooladmin/user_change_password.html', {
        'user': the_user,
        'form': form
    })


@role_login_required(AccessRoles.ADMIN_ROLE)
def user_edit(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()
    if request.method == 'POST':
        form = UserEditForm(request.POST)
        if form.is_valid():
            the_user.first_name = form.cleaned_data['first_name']
            the_user.last_name = form.cleaned_data['last_name']
            the_user.email = form.cleaned_data['email']
            the_user.save()

            message = "User has been updated. "
            old_role = the_user.access_role()
            new_role = form.cleaned_data['role']
            if old_role != new_role:
                message = message + f"User role changes from {old_role} to {new_role}."
                if old_role == AccessRoles.STUDENT_ROLE:
                    # NOT deleting Student here so that we don't lose the data
                    pass
                elif old_role == AccessRoles.PROFESSOR_ROLE:
                    prof = Professor.objects.filter(user_id=the_user.id).get()
                    prof.delete()
                elif old_role == AccessRoles.ADMIN_ROLE:
                    admi = Admin.objects.filter(user_id=the_user.id).get()
                    admi.delete()

                if new_role == AccessRoles.STUDENT_ROLE:
                    stud = Student(user_id=the_user.id, major=form.cleaned_data['major'])
                    stud.save()
                elif new_role == AccessRoles.PROFESSOR_ROLE:
                    prof = Professor(user_id=the_user.id, major=form.cleaned_data['major'])
                    prof.save()
                elif new_role == AccessRoles.ADMIN_ROLE:
                    admi = Admin(user_id=the_user.id)
                    admi.save()
            elif old_role == AccessRoles.STUDENT_ROLE:
                # same role, check if major has to be updated
                stud = Student.objects.filter(user_id=the_user.id).get()
                if stud.major != form.cleaned_data['major']:
                    stud.major = form.cleaned_data['major']
                    stud.save()
            elif old_role == AccessRoles.PROFESSOR_ROLE:
                # same role, check if major has to be updated
                prof = Professor.objects.filter(user_id=the_user.id).get()
                if prof.major != form.cleaned_data['major']:
                    prof.major = form.cleaned_data['major']
                    prof.save()

            messages.success(request, message)
            return redirect('schooladmin:user', userid)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        dict = model_to_dict(the_user)
        dict['role'] = the_user.access_role()
        profs = Professor.objects.filter(user_id=the_user.id)
        studs = Student.objects.filter(user_id=the_user.id)
        if profs.count() > 0:
            dict['major'] = profs[0].major
        elif studs.count() > 0:
            dict['major'] = studs[0].major
        form = UserEditForm(initial=dict)

    return render(request, 'schooladmin/user_edit.html', {
        'user': the_user,
        'original_role': the_user.access_role(),
        'form': form
    })


@role_login_required(AccessRoles.ADMIN_ROLE)
def user_new(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            the_new_user = form.save()
            access_role = form.cleaned_data.get('role')
            major = form.cleaned_data.get('major')
            if access_role == AccessRoles.STUDENT_ROLE:
                student = Student(user=the_new_user,
                                  major=Major.objects.filter(abbreviation=major).get())
                student.save()
            elif access_role == AccessRoles.PROFESSOR_ROLE:
                professor = Professor(user=the_new_user,
                                      major=Major.objects.filter(abbreviation=major).get())
                professor.save()
            elif access_role == AccessRoles.ADMIN_ROLE:
                admin = Admin(user=the_new_user)
                admin.save()
            messages.success(request,
                             f'User {the_new_user.get_full_name()} created as a {access_role}.')
            return redirect('schooladmin:users')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'schooladmin/user_new.html', {'form': form})


# MAJORS


@role_login_required(AccessRoles.ADMIN_ROLE)
def majors(request):
    return render(
        request, 'schooladmin/majors.html',
        filtered_table(
            name='majors',
            qs=Major.objects,
            filter=MajorFilter,
            table=MajorsTable,
            request=request,
        ))


@role_login_required(AccessRoles.ADMIN_ROLE)
def major(request, abbreviation):
    qs = Major.objects.filter(abbreviation=abbreviation)
    if qs.count() < 1:
        return HttpResponse("No such major", reason="Invalid Data", status=404)
    the_major = qs.get()

    data = {
        'major': the_major,
    }
    data.update(
        filtered_table(
            name='profs',
            qs=User.objects.filter(professor__major=the_major),
            filter=UserFilter,
            table=UsersTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='required',
            qs=Course.objects.filter(required_by=the_major),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='offered',
            qs=Course.objects.filter(major=the_major),
            filter=CourseFilter,
            table=CoursesForMajorTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='students',
            qs=User.objects.filter(student__major=the_major),
            filter=UserFilter,
            table=StudentInMajorTable,
            request=request,
        ))

    return render(request, 'schooladmin/major.html', data)


@role_login_required(AccessRoles.ADMIN_ROLE)
def major_edit(request, abbreviation):
    qs = Major.objects.filter(abbreviation=abbreviation)
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
            return redirect('schooladmin:major', abbreviation)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = MajorEditForm(instance=the_major)
    return render(request, 'schooladmin/major_edit.html', {'major': the_major, 'form': form})


@role_login_required(AccessRoles.ADMIN_ROLE)
def major_new(request):
    if request.method == 'POST':
        form = MajorCreationForm(request.POST)
        if form.is_valid():
            the_new_major = form.save()
            message = format_html('Major <a href="{}">{} / {}</a> has been created.',
                                  reverse('schooladmin:major', args=[the_new_major.abbreviation]),
                                  the_new_major.abbreviation, the_new_major.name)
            messages.success(request, message)
            return redirect('schooladmin:majors')
    else:
        form = MajorCreationForm()
    return render(request, 'schooladmin/major_new.html', {'form': form})


@role_login_required(AccessRoles.ADMIN_ROLE)
def courses(request):
    return render(
        request, 'schooladmin/courses.html',
        filtered_table(
            name='courses',
            qs=Course.objects.all(),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
        ))


@role_login_required(AccessRoles.ADMIN_ROLE)
def course(request, courseid):
    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()

    data = {
        'course': the_course,
    }
    data.update(
        filtered_table(
            name='sections',
            qs=Section.objects.filter(course=the_course),
            filter=SectionFilter,
            table=SectionForClassTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='prereqs',
            qs=Course.objects.filter(a_prerequisite__course=the_course),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            page_size=5,
        ))
    data.update(
        filtered_table(
            name='neededby',
            qs=Course.objects.filter(a_course__prerequisite=the_course),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            page_size=10,
        ))

    return render(request, 'schooladmin/course.html', data)


@role_login_required(AccessRoles.ADMIN_ROLE)
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


@role_login_required(AccessRoles.ADMIN_ROLE)
def course_new(request):
    if request.method == 'POST':
        form = CourseCreationForm(request.POST)
        if form.is_valid():
            the_new_course = form.save()
            messages.success(request, f'Course {the_new_course} has been created.')
            return redirect('schooladmin:courses')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = CourseCreationForm()
    return render(request, 'schooladmin/course_new.html', {'form': form})


@role_login_required(AccessRoles.ADMIN_ROLE)
def course_section_new(request, courseid):
    return section_new_helper(request, courseid=courseid)


@role_login_required(AccessRoles.ADMIN_ROLE)
def semesters(request):
    return render(
        request, 'schooladmin/semesters.html',
        filtered_table(
            name='semesters',
            qs=Semester.objects.all(),
            filter=SemesterFilter,
            table=SemestersTable,
            request=request,
        ))


@role_login_required(AccessRoles.ADMIN_ROLE)
def semester(request, semester_id):
    qs = Semester.objects.filter(id=semester_id)
    if qs.count() < 1:
        return HttpResponse("No such semester")
    the_semester = qs.get()

    data = {
        'semester': the_semester,
    }
    data.update(
        filtered_table(
            name='sections',
            qs=Section.objects.filter(semester=the_semester),
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='students',
            qs=the_semester.students_attending(),
            filter=UserFilter,
            table=UsersTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='professors',
            qs=the_semester.professors_teaching(),
            filter=UserFilter,
            table=UsersTable,
            request=request,
        ))

    return render(request, 'schooladmin/semester.html', data)


@role_login_required(AccessRoles.ADMIN_ROLE)
def semester_edit(request, semester_id):
    qs = Semester.objects.filter(id=semester_id)
    if qs.count() < 1:
        return HttpResponse("No such semester")
    the_semester = qs.get()

    if request.method == 'POST':
        form = SemesterEditForm(request.POST, instance=the_semester)
        if form.is_valid():
            the_updated_sem = form.save()
            messages.success(request, f'Semester {the_update_sem} has been updated.')
            return redirect('schooladmin:semester', semester_id)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = SemesterEditForm(instance=the_semester)
    return render(request, 'schooladmin/semester_edit.html', {
        'form': form,
        'semester': the_semester
    })


@role_login_required(AccessRoles.ADMIN_ROLE)
def semester_new(request):
    if request.method == 'POST':
        form = SemesterCreationForm(request.POST)
        if form.is_valid():
            the_new_semester = form.save()
            messages.success(request, f'Semester {the_new_semester} has been created.')
            return redirect('schooladmin:semesters')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = SemesterCreationForm(initial={
            'year': date.today().year,
        })
    return render(request, 'schooladmin/semester_new.html', {'form': form})


@role_login_required(AccessRoles.ADMIN_ROLE)
def semester_section_new(request, semester_id):
    return section_new_helper(request, semester_id=semester_id)


@role_login_required(AccessRoles.ADMIN_ROLE)
def sections(request):
    return render(
        request, 'schooladmin/sections.html',
        filtered_table(
            name='sections',
            qs=Section.objects.all(),
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
        ))


@role_login_required(AccessRoles.ADMIN_ROLE)
def section(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    data = {
        'section': the_section,
    }
    data.update(
        filtered_table(
            name='secstud',
            qs=SectionStudent.objects.filter(section=the_section),
            filter=SectionStudentFilter,
            table=StudentInSectionTable,
            request=request,
        ))

    return render(request, 'schooladmin/section.html', data)


@role_login_required(AccessRoles.ADMIN_ROLE)
def section_students_manage(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    return HttpResponse('not implemented yet')


@role_login_required(AccessRoles.ADMIN_ROLE)
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


@role_login_required(AccessRoles.ADMIN_ROLE)
def section_new_from_section(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()
    return section_new_helper(request,
                              courseid=the_section.course.id,
                              semester_id=the_section.semester.id)


@role_login_required(AccessRoles.ADMIN_ROLE)
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
            'profs': Professor.objects.filter(user__is_active=True),
            'courses': Course.objects.all(),
            'form': form,
        })


@role_login_required(AccessRoles.ADMIN_ROLE)
def sectionstudent(request, id):
    qs = SectionStudent.objects.filter(id=id)
    if qs.count() < 1:
        return HttpResponse("No such sectionstudent")
    the_sectionstud = qs.get()

    return HttpResponse('not implemented yet')
