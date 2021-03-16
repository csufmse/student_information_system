from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User
from sis.models import Student, Admin, Professor, Major


@login_required
def index(request):
    if request.user.access_role() != 'Admin':
        return redirect('sis:access_denied')
    return render(request, 'home_admin.html')


@login_required
def users(request):
    if request.user.access_role() != 'Admin':
        return redirect('sis:access_denied')
    users = [x for x in User.objects.all() if x.access_role() != 'Unknown']
    context = {
        'users': users,
    }
    return render(request, 'users.html', context)


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
                student = Student(
                    user=user,
                    major=Major.objects.filter(abbreviation=major).get())
                student.save()
            elif access_role == 'Professor':
                professor = Professor(
                    user=user,
                    major=Major.objects.filter(abbreviation=major).get())
                professor.save()
            elif access_role == 'Admin':
                admin = Admin(user=user)
                admin.save()
            return redirect('schooladmin:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})
