from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username
        if request.user.is_superuser:
            context = {'is_admin': 'yes'}
            return render(request, 'home_admin.html', context)
        elif request.user.is_staff:
            context = {'is_prof': 'yes'}
            return render(request, 'home_professor.html', context)
        else:
            context = {'is_student': 'yes'}
            return render(request, 'home_student.html', context)


def access_denied(request):
    return render(request, 'access_denied.html', None)
