from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def current_schedule_view(request):
    user = request.user
    if user.is_authenticated and not user.is_superuser and not user.is_staff:
        context = {
             'sections': user.student.sections.all,
             'student_name': user.student.name,
             'logged_in': True,
        }
    else:
        return redirect('/sis/access_denied')
    return render(request, 'student/current_schedule.html', context)
