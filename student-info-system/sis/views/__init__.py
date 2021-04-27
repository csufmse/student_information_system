from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from sis.models import Profile


@login_required
def index(request):
    role = request.user.profile.role
    if role == Profile.ACCESS_ADMIN:
        return redirect('schooladmin:index')
    elif role == Profile.ACCESS_PROFESSOR:
        return redirect('professor:index')
    elif role == Profile.ACCESS_STUDENT:
        return redirect('student:index')


def access_denied(request):
    return render(request, 'sis/access_denied.html', None)
