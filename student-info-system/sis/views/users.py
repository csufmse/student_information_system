from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from sis.models import Profile

@login_required
def user_change_password(request, userid):
    if not userid:
        userid = request.user.id

    # only admin can change the password for someone else
    if request.user.id != userid and request.user.profile.role != Profile.ACCESS_ADMIN:
        messages.error(request, 'Something went wrong.')
        return HttpResponse("Something went wrong.")

    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()

    if request.method == 'POST':
        form = AdminPasswordChangeForm(the_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Password for "{the_user.username}" {the_user.get_full_name()} ' +
                'was successfully updated.')
            return redirect('sis:profile')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = AdminPasswordChangeForm(request.user)
    return render(request, 'sis/user_change_password.html', {
        'user': the_user,
        'form': form
    })

