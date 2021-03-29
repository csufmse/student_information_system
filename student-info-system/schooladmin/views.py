from datetime import date

from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django_tables2 import RequestConfig

from sis.authentication_helpers import role_login_required
from sis.models import (Admin, Course, CoursePrerequisite, Major, Professor, Section, Semester,
                        Student, SectionStudent, AccessRoles)

from .filters import (CourseFilter, MajorFilter, SectionFilter, SemesterFilter, UserFilter)
from .forms import (CourseCreationForm, CourseEditForm, CustomUserCreationForm, MajorCreationForm,
                    MajorEditForm, SectionCreationForm, SectionEditForm, SemesterCreationForm,
                    UserEditForm, SemesterEditForm)
from .tables import (UsersTable, CoursesTable, MajorsTable, SectionsTable, SectionStudentsTable,
                     SemestersTable, FullUsersTable)


@role_login_required(AccessRoles.ADMIN_ROLE)
def index(request):
    return render(request, 'schooladmin/home_admin.html')


# USERS


@role_login_required(AccessRoles.ADMIN_ROLE)
def users(request):
    queryset = User.annotated().all()
    f = UserFilter(request.GET, queryset=queryset)
    has_filter = any(field in request.GET for field in set(f.get_fields()))
    table = FullUsersTable(list(f.qs))
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
    return render(request, 'schooladmin/users.html', {
        'table': table,
        'filter': f,
        'has_filter': has_filter,
    })


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
        elif request.POST.get('enabutton'):
            the_user.is_active = True
            the_user.save()
        return redirect('schooladmin:users')
    return render(request, 'schooladmin/user.html', {'user': the_user})


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
            messages.success(request,
                             f'Password for {the_user.username} was successfully updated.')
            return redirect('schooladmin:user', userid)
        else:
            messages.error(request, 'Please correct the error below.')
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

            old_role = the_user.access_role()
            new_role = form.cleaned_data['role']
            if old_role != new_role:
                if old_role == AccessRoles.STUDENT_ROLE:
                    stud = Student.objects.filter(user_id=the_user.id).get()
                    stud.delete()
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
        form = UserEditForm(dict)
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
            return redirect('schooladmin:users')
    else:
        form = CustomUserCreationForm()
    return render(request, 'schooladmin/user_new.html', {'form': form})


# MAJORS


@role_login_required(AccessRoles.ADMIN_ROLE)
def majors(request):
    queryset = Major.objects.all()
    f = MajorFilter(request.GET, queryset=queryset)
    has_filter = any(field in request.GET for field in set(f.get_fields()))
    table = MajorsTable(list(f.qs))
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
    return render(request, 'schooladmin/majors.html', {
        'table': table,
        'filter': f,
        'has_filter': has_filter,
    })


@role_login_required(AccessRoles.ADMIN_ROLE)
def major(request, abbreviation):
    qs = Major.objects.filter(abbreviation=abbreviation)
    if qs.count() < 1:
        return HttpResponse("No such major", reason="Invalid Data", status=404)
    the_major = qs.get()

    pqueryset = User.objects.filter(professor__major=the_major)
    prof_table = UsersTable(pqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(prof_table)

    rqueryset = Course.objects.filter(required_by=the_major)
    required_table = CoursesTable(rqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(required_table)

    cqueryset = Course.objects.filter(major=the_major)
    course_table = CoursesTable(cqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(course_table)

    return render(request, 'schooladmin/major.html', {
        'major': the_major,
        'profs': prof_table,
        'required': required_table,
        'courses': course_table,
    })


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
            return redirect('schooladmin:majors')
    else:
        form = MajorCreationForm()
    return render(request, 'schooladmin/major_new.html', {'form': form})


@role_login_required(AccessRoles.ADMIN_ROLE)
def courses(request):
    queryset = Course.objects.all()
    f = CourseFilter(request.GET, queryset=queryset)
    has_filter = any(field in request.GET for field in set(f.get_fields()))
    table = CoursesTable(list(f.qs))
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
    return render(request, 'schooladmin/courses.html', {
        'table': table,
        'filter': f,
        'has_filter': has_filter,
    })


@role_login_required(AccessRoles.ADMIN_ROLE)
def course(request, courseid):
    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()

    pqueryset = Course.objects.filter(a_prerequisite__course=the_course)
    ptable = CoursesTable(pqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(ptable)

    nqueryset = Course.objects.filter(a_course__prerequisite=the_course)
    ntable = CoursesTable(nqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(ntable)

    squeryset = Section.objects.filter(course=the_course)
    stable = SectionsTable(squeryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(stable)

    return render(request, 'schooladmin/course.html', {
        'course': the_course,
        'prereqs': ptable,
        'needed_by': ntable,
        'sections': stable,
    })


@role_login_required(AccessRoles.ADMIN_ROLE)
def course_edit(request, courseid):
    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()

    if request.method == 'POST':
        form = CourseEditForm(request.POST, instance=the_course)
        if form.is_valid():
            form.save()
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
            return redirect('schooladmin:courses')
    else:
        form = CourseCreationForm()
    return render(request, 'schooladmin/course_new.html', {'form': form})


@role_login_required(AccessRoles.ADMIN_ROLE)
def course_section_new(request, courseid):
    return section_new_helper(request, courseid=courseid)


@role_login_required(AccessRoles.ADMIN_ROLE)
def semesters(request):
    queryset = Semester.objects.all()
    f = SemesterFilter(request.GET, queryset=queryset)
    has_filter = any(field in request.GET for field in set(f.get_fields()))
    table = SemestersTable(list(f.qs))
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
    return render(request, 'schooladmin/semesters.html', {
        'semesters': table,
        'filter': f,
        'has_filter': has_filter,
    })


@role_login_required(AccessRoles.ADMIN_ROLE)
def semester(request, semester_id):
    qs = Semester.objects.filter(id=semester_id)
    if qs.count() < 1:
        return HttpResponse("No such semester")
    the_semester = qs.get()

    sections_qs = Section.objects.filter(semester=the_semester)
    sections_table = SectionsTable(list(sections_qs))
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(sections_table)

    professors_qs = the_semester.professors_teaching()
    professors_table = UsersTable(professors_qs)
    RequestConfig(request, paginate={"per_page": 10, "page": 1}).configure(professors_table)

    students_qs = the_semester.students_attending()
    students_table = UsersTable(students_qs)
    RequestConfig(request, paginate={"per_page": 15, "page": 1}).configure(students_table)

    return render(
        request, 'schooladmin/semester.html', {
            'semester': the_semester,
            'sections': sections_table,
            'students': students_table,
            'professors': professors_table,
        })


@role_login_required(AccessRoles.ADMIN_ROLE)
def semester_edit(request, semester_id):
    qs = Semester.objects.filter(id=semester_id)
    if qs.count() < 1:
        return HttpResponse("No such semester")
    the_semester = qs.get()

    if request.method == 'POST':
        form = SemesterEditForm(request.POST, instance=the_semester)
        if form.is_valid():
            form.save()
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
            # TODO
            the_new_semester = form.save()
            return redirect('schooladmin:semesters')
    else:
        form = SemesterCreationForm()
    return render(request, 'schooladmin/semester_new.html', {'form': form})


@role_login_required(AccessRoles.ADMIN_ROLE)
def semester_section_new(request, semester_id):
    return section_new_helper(request, semester_id=semester_id)


@role_login_required(AccessRoles.ADMIN_ROLE)
def new_semester(request):
    if request.method == 'POST':
        form = SemesterCreationForm(request.POST)
        if form.is_valid():
            the_new_semester = form.save()
            return redirect('schooladmin:semesters')
    else:
        form = SemesterCreationForm()
    return render(request, 'schooladmin/new_semester.html', {'form': form})


@role_login_required(AccessRoles.ADMIN_ROLE)
def sections(request):
    queryset = Section.objects.all()
    f = SectionFilter(request.GET, queryset=queryset)
    has_filter = any(field in request.GET for field in set(f.get_fields()))
    table = SectionsTable(list(f.qs))
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
    return render(request, 'schooladmin/sections.html', {
        'table': table,
        'filter': f,
        'has_filter': has_filter,
    })


@role_login_required(AccessRoles.ADMIN_ROLE)
def section(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    student_qs = SectionStudent.objects.filter(section=the_section)
    student_table = SectionStudentsTable(list(student_qs))
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(student_table)

    return render(request, 'schooladmin/section.html', {
        'section': the_section,
        'students': student_table
    })


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
            the_new_section = form.save()
            return redirect('schooladmin:section', the_new_section.id)
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

        form = SectionCreationForm(form_values)
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
