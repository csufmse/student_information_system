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
    semester_list = Semester.objects.all().order_by('semester')
    if request.method == 'POST':
        if request.POST.get('semester', False):
            context = {
                'courses': Course.objects.filter(semester=request.POST['semester'])
            }
        if request.POST.get('Register', False):
            student = request.user.student
            section = Section.objects.get(id=request.POST['section'])
            student.sections.add(section)
            return redirect('student:current_schedule')
    else: 
        context = {
            'sections': Section.objects.all().filter(semester=semester_list[0])
        }
    context['semesters'] = semester_list
    return render(request, 'student/registration.html', context)
