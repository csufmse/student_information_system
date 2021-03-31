from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import AccessRoles


@login_required
def index(request):
    access_role = request.user.access_role()
    if access_role == AccessRoles.ADMIN_ROLE:
        return redirect('schooladmin:index')
    elif access_role == AccessRoles.PROFESSOR_ROLE:
        return redirect('professor:index')
    elif access_role == AccessRoles.STUDENT_ROLE:
        return redirect('student:index')


def access_denied(request):
    return render(request, 'sis/access_denied.html', None)
