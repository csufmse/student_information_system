from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render


@login_required
def index(request):
    if request.user.is_authenticated:
        access_role = request.user.access_role()
        if access_role == 'Admin':
            return redirect('schooladmin:index')
        elif access_role == 'Professor':
            return redirect('professor:index')
        elif access_role == 'Student':
            return redirect('student:current_schedule')
    return redirect('sis:access_denied')


def access_denied(request):
    return render(request, 'access_denied.html', None)
