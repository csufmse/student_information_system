from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sis.authentication_helpers import role_login_required
from sis.models import Course, Section


@role_login_required('Student')
def index(request):
    return redirect('student:current_schedule.html')


@role_login_required('Student')
def current_schedule_view(request):
    context = {
        'sections': request.user.student.sections.all,
        'name': request.user.student.name
    }
    return render(request, 'student:current_schedule', context)


@role_login_required('Student')
def registration_view(request):
    #if request.method == 'POST':
    
    context = {'courses': Course.objects.all}
    return render(request, 'student:registration', context)
