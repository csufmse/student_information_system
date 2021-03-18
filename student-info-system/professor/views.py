from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from sis.authentication_helpers import role_login_required


@role_login_required('Professor')
def index(request):
    return render(request, 'home_professor.html')
