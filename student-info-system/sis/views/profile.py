from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from sis.models import (
    Profile,)
from sis.forms.user import UserEditForm
from sis.forms.profile import DemographicForm, UnprivProfileEditForm


@login_required
def profile(request):
    the_user = request.user

    data = {
        'user': the_user,
    }

    if the_user.profile.role == Profile.ACCESS_ADMIN:
        template = 'schooladmin/profile_admin.html'
    elif the_user.profile.role == Profile.ACCESS_PROFESSOR:
        template = 'professor/profile_professor.html'
    elif the_user.profile.role == Profile.ACCESS_STUDENT:
        template = 'student/profile_student.html'
    else:
        messages.error(request, 'something went wrong')
        return redirect('schooladmin:index')

    return render(request, template, data)


@transaction.atomic
@login_required
def profile_edit(request):
    the_user = request.user
    user_profile = the_user.profile
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=the_user, prefix='u')
        profile_form = UnprivProfileEditForm(request.POST, instance=user_profile, prefix='p')
        demo_form = DemographicForm(request.POST, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid() and demo_form.is_valid():
            user_form.save()
            profile_form.save()
            demo_form.save()
            messages.success(request, "Profile has been updated.")
            return profile(request)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        user_form = UserEditForm(instance=the_user, prefix='u')
        profile_form = UnprivProfileEditForm(instance=user_profile, prefix='p')
        demo_form = DemographicForm(instance=user_profile,)

    return render(
        request, 'student/student_edit.html', {
            'user': the_user,
            'user_form': user_form,
            'profile_form': profile_form,
            'demo_form': demo_form,
        })
