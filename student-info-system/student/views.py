from django.shortcuts import render
from django.http import HttpResponse


def current_schedule_view(request):
    return render(request, 'student/current_schedule.html', None)
