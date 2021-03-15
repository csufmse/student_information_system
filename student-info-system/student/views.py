from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    if request.user.access_role() != 'Student':
        return redirect('sis:access_denied')
    return redirect('student:current_schedule')

@login_required
def current_schedule_view(request):
    if request.user.access_role() != 'Student':
        return redirect('sis:access_denied')
    context = {
             'sections': request.user.student.sections.all,
             'student_name': request.user.student.name,
             'logged_in': True,
        }
    return render(request, 'student/current_schedule.html', context)
