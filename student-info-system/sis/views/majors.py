from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from sis.authentication_helpers import role_login_required

from sis.models import (Major, Professor, Section, Semester, Student, Course, Profile)

from sis.utils import filtered_table2, DUMMY_ID, next_prev

from sis.filters.course import CourseFilter
from sis.filters.major import MajorFilter
from sis.filters.user import StudentFilter, UserFilter, ProfessorFilter

from sis.tables.courses import CoursesTable, CoursesForMajorTable, MajorCoursesMetTable
from sis.tables.majors import MajorsTable
from sis.tables.users import UsersTable, FullUsersTable, StudentsTable, StudentInMajorTable


def majors(request):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role
    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN

    data = {
        'can_add': is_admin,
    }
    data.update(
        filtered_table2(
            name='majors',
            qs=Major.objects,
            filter=MajorFilter,
            table=MajorsTable,
            request=request,
            scrollable=True,
            self_url=reverse('sis:majors'),
            click_url=reverse('sis:major', args=[DUMMY_ID]),
        ))
    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}
    return render(request, 'sis/majors.html', data)


def major(request, majorid):
    the_user = request.user
    logged_in = request.user.is_authenticated
    is_admin = logged_in and the_user.profile.role == Profile.ACCESS_ADMIN

    include_students = logged_in and the_user.profile.role in (Profile.ACCESS_ADMIN,
                                                               Profile.ACCESS_PROFESSOR)

    qs = Major.objects.filter(id=majorid)
    if qs.count() < 1:
        messages.error(request, "Something went wrong.")
        return HttpResponse("No such major", reason="Invalid Data", status=404)

    the_major = qs.get()

    data = {
        'major': the_major,
        'permit_edit': is_admin,
        'include_students': include_students,
    }
    data.update(next_prev(request, 'majors', majorid))
    data.update(
        filtered_table2(
            name='profs',
            qs=User.objects.all().filter(profile__professor__major=the_major),
            filter=UserFilter,
            table=UsersTable,
            request=request,
            self_url=reverse('sis:major', args=[majorid]),
            click_url=reverse('schooladmin:professor', args=[DUMMY_ID]),
        ))

    data.update(
        filtered_table2(
            name='required',
            qs=Course.objects.filter(required_by=the_major),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            self_url=reverse('sis:major', args=[majorid]),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))

    data.update(
        filtered_table2(
            name='offered',
            qs=Course.objects.filter(major=the_major),
            filter=CourseFilter,
            table=CoursesForMajorTable,
            request=request,
            self_url=reverse('sis:major', args=[majorid]),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))

    if include_students:
        data.update(
            filtered_table2(
                name='students',
                qs=User.objects.all().filter(profile__student__major=the_major),
                filter=UserFilter,
                table=StudentInMajorTable,
                request=request,
                self_url=reverse('sis:major', args=[majorid]),
                click_url=reverse('schooladmin:student', args=[DUMMY_ID]),
            ))

    if not logged_in:
        data['user'] = {'home_template': "schooladmin/home_guest.html"}
    return render(request, 'sis/major.html', data)
