from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.http import HttpResponse
from django import forms
from django.shortcuts import render, redirect
from django_tables2 import RequestConfig
from django_filters import (FilterSet, CharFilter, ChoiceFilter, ModelChoiceFilter,
                            ModelMultipleChoiceFilter)

from sis.authentication_helpers import role_login_required
from sis.models import Student, Admin, Professor, Major, Course
from .forms import CustomUserCreationForm, MajorCreationForm
from .tables import UsersTable, MajorsTable, BasicProfsTable, BasicCoursesTable


@role_login_required('Admin')
def index(request):
    return render(request, 'home_admin.html')


# USERS ####
class UserFilter(FilterSet):
    username = CharFilter(lookup_expr='icontains')
    name = CharFilter(field_name='name', label='Name', lookup_expr='icontains')
    access_role = ChoiceFilter(field_name='access_role',
                               label='Access Role',
                               choices=(('Admin', 'Admin'), ('Professor', 'Professor'),
                                        ('Student', 'Student')))
    #    is_active = BooleanFilter(field_name='is_active',label="User Enabled")
    is_active = ChoiceFilter(label='Enabled?', choices=((True, 'Enabled'), (False, 'Disabled')))

    class Meta:
        model = User
        fields = ['username', 'name', 'access_role', 'is_active']


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
def new_user(request):
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
                student = Student(user=user, major=Major.objects.filter(abbreviation=major).get())
                student.save()
            elif access_role == 'Professor':
                professor = Professor(user=user,
                                      major=Major.objects.filter(abbreviation=major).get())
                professor.save()
            elif access_role == 'Admin':
                admin = Admin(user=the_new_user)
                admin.save()
            return redirect('schooladmin:users')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


# MAJORS ####
class MajorFilter(FilterSet):
    abbreviation = CharFilter(field_name='abbreviation', lookup_expr='icontains')
    name = CharFilter(field_name='name', label='Name contains', lookup_expr='icontains')
    description = CharFilter(field_name='description',
                             label='Description contains',
                             lookup_expr='icontains')
    # professors = ModelChoiceFilter(queryset=Professor.objects.filter(),
    #                               field_name='professor__user__last_name',
    #                               lookup_expr='icontains',label='Has Professor')
    professors = CharFilter(field_name='professor__user__last_name',
                            lookup_expr='icontains',
                            label='Has Professor')

    # requires = ModelChoiceFilter(field_name='requires',lookup_field='required_by',)

    class Meta:
        model = Major
        fields = [
            'abbreviation',
            'name',
            'description',
            'professors',
            # 'requires'
        ]


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
def new_major(request):
    if request.method == 'POST':
        form = MajorCreationForm(request.POST)
        if form.is_valid():
            the_new_major = form.save()
            return redirect('schooladmin:majors')
    else:
        form = MajorCreationForm()
    return render(request, 'new_major.html', {'form': form})


@role_login_required('Admin')
def course(request, courseid):
    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()
    return HttpResponse("Sure, " + the_course.name + " is a real thing.")
