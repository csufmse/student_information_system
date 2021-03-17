from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django_tables2 import SingleTableMixin, RequestConfig
from django_filters import FilterSet, CharFilter, ChoiceFilter, BooleanFilter
from django_filters.views import FilterView

from sis.models import Student, Admin, Professor, Major
from .forms import CustomUserCreationForm
from .tables import UsersTable


@login_required
def index(request):
    if request.user.access_role() != 'Admin':
        return redirect('sis:access_denied')
    return render(request, 'home_admin.html')


class UserFilter(FilterSet):
    username = CharFilter(lookup_expr='iexact')
    name = CharFilter(field_name='name', label='Name', lookup_expr='icontains')
    access_role = ChoiceFilter(field_name='access_role',
                               label='Access Role',
                               choices=(('Admin', 'Admin'), ('Professor', 'Professor'),
                                        ('Student', 'Student')))
    #    is_active = BooleanFilter(field_name='is_active',label="User Enabled")
    is_active = ChoiceFilter(choices=((True, 'Enabled'), (False, 'Disabled')))

    class Meta:
        model = User
        fields = ['username', 'name', 'access_role', 'is_active']


@login_required
def users(request):
    if request.user.access_role() != 'Admin':
        return redirect('sis:access_denied')
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


@login_required
def new_user(request):
    if request.user.access_role() != 'Admin':
        return redirect('sis:access_denied')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            access_role = form.cleaned_data.get('role')
            major = form.cleaned_data.get('major')
            if access_role == 'Student':
                student = Student(user=user, major=Major.objects.filter(abbreviation=major).get())
                student.save()
            elif access_role == 'Professor':
                professor = Professor(user=user,
                                      major=Major.objects.filter(abbreviation=major).get())
                professor.save()
            elif access_role == 'Admin':
                admin = Admin(user=user)
                admin.save()
            return redirect('schooladmin:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def user(request, userid):
    if request.user.access_role() != 'Admin':
        return redirect('sis:access_denied')
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    theUser = qs.get()
    if request.method == 'POST':
        if request.POST.get('disbutton'):
            theUser.is_active = False
            theUser.save()
        elif request.POST.get('enabutton'):
            theUser.is_active = True
            theUser.save()
        return redirect('schooladmin:users')
    return render(request, 'user.html', {'user': theUser})
