from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    if request.user.access_role() != 'Professor':
        return redirect('sis:access_denied')
    return render(request, 'home_professor.html')
