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
    context = {}
    semester_list = Semester.objects.all()

    if request.method == 'POST':
        if request.POST.get('semester', False):
            sections = Section.objects.filter(semester=request.POST['semester'])
            context['sections'] = sections
        if request.POST.get('course', False):
            student = request.user.student
            reg_section = Section.objects.get(
                id=request.POST[request.POST['course']])
            student.sections.add(reg_section)
            return redirect('student:current_schedule')

    if len(semester_list):
        if 'sections' not in context:
            sections = Section.objects.filter(semester=semester_list[0])
            context['sections'] = sections
        courses = set(section.course for section in sections)
        context['semesters'] = semester_list
        context['courses'] = courses
    return render(request, 'student/registration.html', context)
