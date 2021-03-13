from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound 

def current_schedule_view(request):
    if request.user.is_authenticated and not request.user.is_superuser and not request.user.is_staff:
         context = {
             'sections': request.user.student.sections.all,
             'logged_in': True,
         }
    else:
        return redirect('/accounts/login/')
    return render(request, 'student/current_schedule.html', context)
