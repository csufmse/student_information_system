from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from sis.authentication_helpers import role_login_required


@role_login_required('Professor')
def index(request):
    return render(request, 'home_professor.html')


@login_required
def courses(request):
    if request.user.access_role() != 'Professor':
        return redirect('sis:access_denied')
    courses = [x for x in Course.objects.all() if x.access_role() != 'Unknown']
    context = {
        'courses': courses,
    }
    return render(request, 'courses_professor.html', context)
