from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from sis.forms import SignUpForm


def index(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username
    return HttpResponse("You're at SIS root page. User name = " + username)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def current_courses(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username
    return HttpResponse(
        "You better be logged in, showing your current courses. User name = " +
        username)


def majors(request):
    return HttpResponse("Don't need to be logged in, showing majors.")


@login_required
def section_edit(request):
    return HttpResponse("Logged in + section_edit. Edit a section here!")
