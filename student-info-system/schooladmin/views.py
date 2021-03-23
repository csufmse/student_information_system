from datetime import date
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_tables2 import RequestConfig
from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.forms.models import model_to_dict

from django.contrib.auth.models import User
from sis.authentication_helpers import role_login_required
from sis.models import (Student, Admin, Professor, Major, Course, CoursePrerequisite, Semester,
                        Section)
from .forms import (CustomUserCreationForm, UserEditForm, MajorCreationForm, MajorEditForm,
                    SectionCreationForm, SectionEditForm, SemesterCreationForm, CourseEditForm,
                    CourseCreationForm)
from .tables import (UsersTable, MajorsTable, BasicProfsTable, BasicCoursesTable, SemestersTable,
                     CoursesTable, SectionsTable, SectionStudentsTable)
from .filters import UserFilter, MajorFilter, SemesterFilter, SectionFilter, CourseFilter


@role_login_required('Admin')
def index(request):
    return render(request, 'home_admin.html')


# USERS


@role_login_required('Admin')
def users(request):
    queryset = User.annotated().all()
    f = UserFilter(request.GET, queryset=queryset)
    has_filter = any(field in request.GET for field in set(f.get_fields()))
    table = UsersTable(f.qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
    return render(request, 'users.html', {
        'table': table,
        'filter': f,
        'has_filter': has_filter,
    })


@role_login_required('Admin')
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
    return render(request, 'user.html', {'user': the_user})


@role_login_required('Admin')
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
    return render(request, 'user_change_password.html', {'user': the_user, 'form': form})


@role_login_required('Admin')
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
                if old_role == 'Student':
                    stud = Student.objects.filter(user_id=the_user.id).get()
                    stud.delete()
                elif old_role == 'Professor':
                    prof = Professor.objects.filter(user_id=the_user.id).get()
                    prof.delete()
                elif old_role == 'Admin':
                    admi = Admin.objects.filter(user_id=the_user.id).get()
                    admi.delete()

                if new_role == 'Student':
                    stud = Student(user_id=the_user.id, major=form.cleaned_data['major'])
                    stud.save()
                elif new_role == 'Professor':
                    prof = Professor(user_id=the_user.id, major=form.cleaned_data['major'])
                    prof.save()
                elif new_role == 'Admin':
                    admi = Admin(user_id=the_user.id)
                    admi.save()
            elif old_role == 'Student':
                # same role, check if major has to be updated
                stud = Student.objects.filter(user_id=the_user.id).get()
                if stud.major != form.cleaned_data['major']:
                    stud.major = form.cleaned_data['major']
                    stud.save()
            elif old_role == 'Professor':
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
    return render(request, 'user_edit.html', {
        'user': the_user,
        'original_role': the_user.access_role(),
        'form': form
    })


@role_login_required('Admin')
def user_new(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            the_new_user = form.save()
            access_role = form.cleaned_data.get('role')
            major = form.cleaned_data.get('major')
            if access_role == 'Student':
                student = Student(user=the_new_user,
                                  major=Major.objects.filter(abbreviation=major).get())
                student.save()
            elif access_role == 'Professor':
                professor = Professor(user=the_new_user,
                                      major=Major.objects.filter(abbreviation=major).get())
                professor.save()
            elif access_role == 'Admin':
                admin = Admin(user=the_new_user)
                admin.save()
            return redirect('schooladmin:users')
    else:
        form = CustomUserCreationForm()
    return render(request, 'user_new.html', {'form': form})


# MAJORS


@role_login_required('Admin')
def majors(request):
    queryset = Major.objects.all()
    f = MajorFilter(request.GET, queryset=queryset)
    has_filter = any(field in request.GET for field in set(f.get_fields()))
    table = MajorsTable(f.qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
    return render(request, 'majors.html', {
        'table': table,
        'filter': f,
        'has_filter': has_filter,
    })


@role_login_required('Admin')
def major(request, abbreviation):
    qs = Major.objects.filter(abbreviation=abbreviation)
    if qs.count() < 1:
        return HttpResponse("No such major")
    the_major = qs.get()

    pqueryset = User.objects.filter(professor__major=the_major)
    prof_table = BasicProfsTable(pqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(prof_table)

    rqueryset = Course.objects.filter(required_by=the_major)
    required_table = BasicCoursesTable(rqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(required_table)

    cqueryset = Course.objects.filter(major=the_major)
    course_table = BasicCoursesTable(cqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(course_table)

    return render(request, 'major.html', {
        'major': the_major,
        'profs': prof_table,
        'required': required_table,
        'courses': course_table,
    })


@role_login_required('Admin')
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
    return render(request, 'major_edit.html', {'form': form})


@role_login_required('Admin')
def major_new(request):
    if request.method == 'POST':
        form = MajorCreationForm(request.POST)
        if form.is_valid():
            the_new_major = form.save()
            return redirect('schooladmin:majors')
    else:
        form = MajorCreationForm()
    return render(request, 'major_new.html', {'form': form})


@role_login_required('Admin')
def courses(request):
    queryset = Course.objects.all()
    f = CourseFilter(request.GET, queryset=queryset)
    has_filter = any(field in request.GET for field in set(f.get_fields()))
    table = CoursesTable(f.qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
    return render(request, 'courses.html', {
        'table': table,
        'filter': f,
        'has_filter': has_filter,
    })


@role_login_required('Admin')
def course(request, courseid):
    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()

    pqueryset = Course.objects.filter(a_prerequisite__course=the_course)
    ptable = BasicCoursesTable(pqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(ptable)

    nqueryset = Course.objects.filter(a_course__prerequisite=the_course)
    ntable = BasicCoursesTable(nqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(ntable)

    return render(request, 'course.html', {
        'course': the_course,
        'prereqs': ptable,
        'needed_by': ntable,
    })


@role_login_required('Admin')
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
    return render(request, 'course_edit.html', {'form': form})


@role_login_required('Admin')
def course_new(request):
    if request.method == 'POST':
        form = CourseCreationForm(request.POST)
        if form.is_valid():
            the_new_course = form.save()
            return redirect('schooladmin:courses')
    else:
        form = CourseCreationForm()
    return render(request, 'course_new.html', {'form': form})


@role_login_required('Admin')
def course_section_new(request, courseid):
    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()
    form_values = {'course': the_course}
    semesters = Semester.objects.order_by('-date_registration_opens').filter(
        date_registration_opens__lte=date.today(), date_last_drop__gte=date.today())
    if semesters.count() > 0:
        form_values['semester'] = semesters[0]

    form = SectionCreationForm(form_values)
    return render(request, 'section_new.html', {'form': form})


@role_login_required('Admin')
def semesters(request):
    if request.user.access_role() != 'Admin':
        return redirect('sis:access_denied')
    queryset = Semester.objects.all()
    f = SemesterFilter(request.GET, queryset=queryset)
    has_filter = any(field in request.GET for field in set(f.get_fields()))
    table = SemestersTable(f.qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
    return render(request, 'semesters.html', {
        'table': table,
        'filter': f,
        'has_filter': has_filter,
    })


@role_login_required('Admin')
def semester(request, semester_id):
    if request.user.access_role() != 'Admin':
        return redirect('sis:access_denied')
    qs = Semester.objects.filter(id=semester_id)
    if qs.count() < 1:
        return HttpResponse("No such semester")
    the_semester = qs.get()

    sections_qs = Section.objects.filter(semester=the_semester)
    sections_table = SectionsTable(sections_qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(sections_table)

    return render(request, 'semester.html', {
        'semester': the_semester,
        'sections': sections_table
    })


@role_login_required('Admin')
def semester_section_new(request, semester_id):
    qs = Semester.objects.filter(id=semester_id)
    if qs.count() < 1:
        return HttpResponse("No such semester")
    the_semester = qs.get()
    form_values = {'semester': the_semester}
    form = SectionCreationForm(form_values)
    return render(request, 'section_new.html', {'form': form})


@role_login_required('Admin')
def new_semester(request):
    if request.user.access_role() != 'Admin':
        return redirect('sis:access_denied')
    if request.method == 'POST':
        form = SemesterCreationForm(request.POST)
        if form.is_valid():
            the_new_semester = form.save()
            return redirect('schooladmin:semesters')
    else:
        form = SemesterCreationForm()
    return render(request, 'new_semester.html', {'form': form})


@role_login_required('Admin')
def sections(request):
    queryset = Section.objects.all()
    f = SectionFilter(request.GET, queryset=queryset)
    has_filter = any(field in request.GET for field in set(f.get_fields()))
    table = SectionsTable(f.qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(table)
    return render(request, 'sections.html', {
        'table': table,
        'filter': f,
        'has_filter': has_filter,
    })


@role_login_required('Admin')
def section(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    student_qs = Student.objects.filter(sectionstudent__section=the_section)
    student_table = SectionStudentsTable(student_qs)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(student_table)

    return render(request, 'section.html', {'section': the_section, 'students': student_table})


@role_login_required('Admin')
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
    return render(request, 'section_edit.html', {'form': form, 'section': the_section})


@role_login_required('Admin')
def section_new(request):
    if request.method == 'POST':
        form = SectionCreationForm(request.POST)
        if form.is_valid():
            the_new_section = form.save()
            return redirect('schooladmin:sections')
    else:
        form = SectionCreationForm(request.GET)
    return render(request, 'section_new.html', {'form': form})
