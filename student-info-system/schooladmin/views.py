from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_tables2 import RequestConfig
from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.forms.models import model_to_dict

from sis.authentication_helpers import role_login_required
from django.contrib.auth.models import User
from sis.models import Student, Admin, Professor, Major, Course, Semester
from .forms import CustomUserCreationForm, MajorCreationForm, MajorEditForm, UserEditForm, SemesterCreationForm
from .tables import UsersTable, MajorsTable, BasicProfsTable, BasicCoursesTable, SemestersTable
from .filters import UserFilter, MajorFilter, SemesterFilter


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
    #    cqueryset = Course.objects.filter(a_prerequisite__course__major=the_major)
    cqueryset = Course.objects.filter(required_by=the_major)
    course_table = BasicCoursesTable(cqueryset)
    RequestConfig(request, paginate={"per_page": 25, "page": 1}).configure(course_table)
    # if request.method == 'POST':
    #     if request.POST.get('disbutton'):
    #         the_user.is_active = False
    #         the_user.save()
    #     elif request.POST.get('enabutton'):
    #         the_user.is_active = True
    #         the_user.save()
    #     return redirect('schooladmin:users')
    return render(request, 'major.html', {
        'major': the_major,
        'profs': prof_table,
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
            form.save()
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
def course(request, courseid):
    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()
    return HttpResponse("Sure, " + the_course.name + " is a real thing.")


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
    # if request.method == 'POST':
    #     if request.POST.get('disbutton'):
    #         the_user.is_active = False
    #         the_user.save()
    #     elif request.POST.get('enabutton'):
    #         the_user.is_active = True
    #         the_user.save()
    #     return redirect('schooladmin:users')
    return render(request, 'semester.html', {'semester': the_semester})


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
