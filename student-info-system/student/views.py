from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sis.authentication_helpers import role_login_required
from sis.models import Course, Section, Semester


@role_login_required('Student')
def index(request):
    return redirect('student:current_schedule.html')


@role_login_required('Student')
def current_schedule_view(request):
    context = {
        'sections': request.user.student.sections.all,
        'name': request.user.student.name
    }
    return render(request, 'student/current_schedule.html', context)


@role_login_required('Student')
def registration_view(request):
    if request.method == 'POST':
        if request.POST['semester']:
            context = {
                'courses': Course.objects.filter(section_set=request.POST['semester'])
            }
        if request.POST['Register']:
            user.student.sections.add(request.POST[section])
            return redurect('student:current_schedule'
    else: 
        context = {
            'courses': Course.objects.all
        }
    context['semesters'] = Semester.objects.all().order_by('name')
    return render(request, 'student/registration.html', context)
