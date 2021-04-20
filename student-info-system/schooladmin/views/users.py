from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from sis.authentication_helpers import role_login_required

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, Semester, Student,
                        SectionStudent, Profile, Message)

from sis.forms.profile import DemographicForm, ProfileCreationForm, ProfileEditForm
from sis.forms.student import StudentEditForm, StudentCreationForm
from sis.forms.user import UserCreationForm, UserEditForm
from sis.forms.professor import ProfessorCreationForm, ProfessorEditForm

from sis.utils import filtered_table2, DUMMY_ID
from sis.filters.course import CourseFilter
from sis.filters.message import (FullSentMessageFilter, FullReceivedMessageFilter,
                                 SentMessageFilter, ReceivedMessageFilter)
from sis.filters.referenceitem import ItemFilter
from sis.filters.section import SectionFilter
from sis.filters.sectionstudent import SectionStudentFilter
from sis.filters.semester import SemesterFilter
from sis.filters.user import StudentFilter, UserFilter, ProfessorFilter
from sis.tables.courses import CoursesTable, CoursesForMajorTable, MajorCoursesMetTable
from sis.tables.messages import MessageSentTable, MessageReceivedTable
from sis.tables.referenceitems import ProfReferenceItemsTable
from sis.tables.sections import SectionForClassTable, SectionsTable
from sis.tables.sectionstudents import (StudentHistoryTable, StudentInSectionTable)
from sis.tables.semesters import SemestersSummaryTable, SemestersTable
from sis.tables.users import (UsersTable, FullUsersTable, StudentsTable, StudentInMajorTable,
                              ProfessorsTable)

from sis.tables.courses import CoursesTable, CoursesForMajorTable, MajorCoursesMetTable
from sis.tables.sections import SectionForClassTable, SectionsTable
from sis.tables.sectionstudents import (StudentHistoryTable, StudentInSectionTable)
from sis.tables.semesters import SemestersSummaryTable, SemestersTable
from sis.tables.users import (UsersTable, FullUsersTable, StudentsTable, StudentInMajorTable,
                              ProfessorsTable)


@role_login_required(Profile.ACCESS_ADMIN)
def userslist(request):
    return render(
        request, 'schooladmin/users.html',
        filtered_table2(
            name='users',
            qs=User.objects.exclude(profile__role=Profile.ACCESS_NONE),
            filter=UserFilter,
            table=FullUsersTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:users'),
            click_url=reverse('schooladmin:user', args=[DUMMY_ID]),
        ))


def user(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()

    is_admin = request.user.profile.role == Profile.ACCESS_ADMIN

    if is_admin and request.method == 'POST':
        if request.POST.get('disbutton'):
            the_user.is_active = False
            the_user.save()
            messages.success(request,
                             f'User {the_user.get_full_name()} has been disabled from login.')
        elif request.POST.get('enabutton'):
            the_user.is_active = True
            the_user.save()
            messages.success(request,
                             f'User {the_user.get_full_name()} has been enabled for login.')
        return redirect('schooladmin:users')

    if the_user.profile.role == Profile.ACCESS_STUDENT:
        return student(request, userid)
    elif the_user.profile.role == Profile.ACCESS_PROFESSOR:
        return professor(request, userid)

    data = {
        'auser': the_user,
        'show_all': is_admin,
    }
    if is_admin:
        data.update(
            filtered_table2(
                name='received',
                qs=the_user.profile.sent_to.all(),
                filter=FullReceivedMessageFilter,
                table=MessageReceivedTable,
                request=request,
                wrap_list=False,
                self_url=reverse('schooladmin:user', args=[userid]),
            ))
        data.update(
            filtered_table2(
                name='sent',
                qs=the_user.profile.sent_by.all(),
                filter=FullSentMessageFilter,
                table=MessageSentTable,
                request=request,
                wrap_list=False,
                self_url=reverse('schooladmin:user', args=[userid]),
            ))

    return render(request, 'schooladmin/user.html', data)


@transaction.atomic
@login_required
def user_edit(request, userid):
    # only admin can edit someone else
    if request.user.id != userid and request.user.profile.role != Profile.ACCESS_ADMIN:
        messages.error(request, 'Something went wrong.')
        return HttpResponse("Something went wrong.")

    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=the_user, prefix='u')
        profile = the_user.profile
        profile_form = ProfileEditForm(request.POST, instance=profile, prefix='p')
        demo_form = DemographicForm(
            request.POST,
            instance=profile,
        )
        if user_form.is_valid() and profile_form.is_valid() and demo_form.is_valid():
            the_new_user = user_form.save()
            the_profile = profile_form.save()
            demo_form.save()

            message = "User has been updated. "

            success = True
            # new model just adds the student/professor object if needed. this way
            # we don't lose the info from the previous role.
            if the_profile.role == Profile.ACCESS_STUDENT:
                if the_profile.has_student():
                    the_stud = the_profile.student
                else:
                    the_stud = Student.objects.create(profile=the_profile)
                student_form = StudentEditForm(request.POST, instance=the_stud)

                if student_form.is_valid():
                    stud = student_form.save(commit=False)
                    stud.profile = the_profile
                    stud.save()
                else:
                    success = False

            elif the_profile.role == Profile.ACCESS_PROFESSOR:
                if the_profile.has_professor():
                    the_prof = the_profile.professor
                else:
                    the_prof = Professor.objects.create(profile=the_profile)
                professor_form = ProfessorEditForm(request.POST, instance=the_prof)

                if professor_form.is_valid():
                    prof = professor_form.save(commit=False)
                    prof.profile = the_profile
                    prof.save()
                else:
                    success = False

            if success:
                messages.success(request, message)
                return redirect('schooladmin:user', userid)
            else:
                messages.error(request, 'Please correct the error(s) below.')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        user_form = UserEditForm(instance=the_user, prefix='u')
        profile = the_user.profile
        profile_form = ProfileEditForm(instance=profile, prefix='p')
        demo_form = DemographicForm(instance=profile,)
        try:
            stud = profile.student
            student_form = StudentEditForm(instance=stud)
        except Exception:
            student_form = StudentEditForm(initial={})

        try:
            prof = profile.professor
            professor_form = ProfessorEditForm(instance=prof)
        except Exception:
            professor_form = ProfessorEditForm(initial={})

    return render(
        request, 'schooladmin/user_edit.html', {
            'auser': the_user,
            'original_role': the_user.profile.role,
            'user_form': user_form,
            'profile_form': profile_form,
            'demo_form': demo_form,
            'student_form': student_form,
            'professor_form': professor_form,
        })


@transaction.atomic
@role_login_required(Profile.ACCESS_ADMIN)
def user_new(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST, prefix='u')
        profile_form = ProfileCreationForm(request.POST, prefix='p')

        if user_form.is_valid() and profile_form.is_valid():
            the_new_user = user_form.save()
            the_new_profile = profile_form.save(commit=False)
            the_new_profile.user = the_new_user
            the_new_profile.save()

            access_role = the_new_profile.role
            success = True
            if access_role == Profile.ACCESS_STUDENT:
                student_form = StudentCreationForm(request.POST, prefix='s')
                if student_form.is_valid():
                    student = student_form.save(commit=False)
                    student.profile = the_new_profile
                    student.save()
                else:
                    success = False
            elif access_role == Profile.ACCESS_PROFESSOR:
                professor_form = ProfessorCreationForm(request.POST, prefix='r')
                if professor_form.is_valid():
                    professor = professor_form.save(commit=False)
                    professor.profile = the_new_profile
                    professor.save()
                else:
                    success = False

            if success:
                messages.success(
                    request, f'User {the_new_user.get_full_name()} created ' +
                    f'as a {the_new_user.profile.rolename}.')
                return redirect('schooladmin:users')
            else:
                messages.error(request, 'Please correct the error(s) below.')
        else:
            professor_form = ProfessorCreationForm(request.POST, prefix='r')
            student_form = StudentCreationForm(request.POST, prefix='s')

            messages.error(request, 'Please correct the error(s) below.')
    else:
        user_form = UserCreationForm(prefix='u')
        profile_form = ProfileCreationForm(prefix='p')
        student_form = StudentCreationForm(prefix='s')
        professor_form = ProfessorCreationForm(prefix='r')

    return render(
        request, 'schooladmin/user_new.html', {
            'user_form': user_form,
            'profile_form': profile_form,
            'student_form': student_form,
            'professor_form': professor_form
        })


@role_login_required(Profile.ACCESS_ADMIN, Profile.ACCESS_PROFESSOR)
def student(request, userid):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role
    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN

    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()

    if the_user.profile.role != Profile.ACCESS_STUDENT:
        return user(request, userid)

    if request.method == 'POST':
        if request.POST.get('disbutton'):
            the_user.is_active = False
            the_user.save()
        elif request.POST.get('enabutton'):
            the_user.is_active = True
            the_user.save()
        return redirect('schooladmin:users')

    data = {
        'auser': the_user,
        'can_edit': is_admin,
    }
    data.update(
        filtered_table2(
            name='semesters',
            qs=the_user.profile.student.semesters.all(),
            filter=SemesterFilter,
            table=SemestersSummaryTable,
            request=request,
            self_url=reverse('schooladmin:student', args=[userid]),
            click_url=reverse('schooladmin:semester', args=[DUMMY_ID]),
        ))

    data.update(
        filtered_table2(
            name='history',
            qs=the_user.profile.student.course_history(),
            filter=SectionStudentFilter,
            table=StudentHistoryTable,
            request=request,
            self_url=reverse('schooladmin:student', args=[userid]),
            click_url=reverse('schooladmin:sectionstudent', args=[DUMMY_ID]),
        ))

    data.update(
        filtered_table2(
            name='remaining',
            qs=the_user.profile.student.remaining_required_courses(),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            self_url=reverse('schooladmin:student', args=[userid]),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))
    data.update(
        filtered_table2(
            name='majorcourses',
            qs=the_user.profile.student.requirements_met_list(),
            filter=CourseFilter,
            table=MajorCoursesMetTable,
            request=request,
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))
    if is_admin:
        data.update(
            filtered_table2(
                name='received',
                qs=the_user.profile.sent_to.filter(time_archived__isnull=True),
                filter=ReceivedMessageFilter,
                table=MessageReceivedTable,
                request=request,
                wrap_list=False,
                self_url=reverse('schooladmin:student', args=[userid]),
            ))
        data.update(
            filtered_table2(
                name='sent',
                qs=the_user.profile.sent_by.filter(time_archived__isnull=True),
                filter=SentMessageFilter,
                table=MessageSentTable,
                request=request,
                wrap_list=False,
                self_url=reverse('schooladmin:student', args=[userid]),
            ))

    return render(request, 'schooladmin/student.html', data)


def professor(request, userid):
    logged_in = request.user.is_authenticated
    if logged_in:
        user_role = request.user.profile.role
    is_admin = logged_in and user_role == Profile.ACCESS_ADMIN
    if logged_in:
        the_user = request.user

    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_prof = qs[0]

    if is_admin and request.method == 'POST':
        if request.POST.get('disbutton'):
            the_prof.is_active = False
            the_prof.save()
        elif request.POST.get('enabutton'):
            the_prof.is_active = True
            the_prof.save()
        return redirect('schooladmin:users')

    data = {'auser': the_prof, 'can_edit': is_admin}
    data.update(
        filtered_table2(
            name='semesters',
            qs=the_prof.profile.professor.semesters_teaching(),
            filter=SemesterFilter,
            table=SemestersSummaryTable,
            request=request,
            self_url=reverse('schooladmin:professor', args=[userid]),
            click_url=reverse('schooladmin:semester', args=[DUMMY_ID]),
        ))

    data.update(
        filtered_table2(
            name='sections',
            qs=the_prof.profile.professor.section_set,
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
            self_url=reverse('schooladmin:professor', args=[userid]),
            click_url=reverse('schooladmin:section', args=[DUMMY_ID]),
        ))

    data.update(
        filtered_table2(
            name='items',
            qs=the_prof.profile.professor.referenceitem_set,
            filter=ItemFilter,
            table=ProfReferenceItemsTable,
            request=request,
            self_url=reverse('schooladmin:professor', args=[userid]),
            click_url=reverse('schooladmin:professor_item', args=[userid, DUMMY_ID]),
        ))
    if is_admin:
        data.update(
            filtered_table2(
                name='received',
                qs=the_prof.profile.sent_to.filter(time_archived__isnull=True),
                filter=ReceivedMessageFilter,
                table=MessageReceivedTable,
                request=request,
                wrap_list=False,
                self_url=reverse('schooladmin:professor', args=[userid]),
            ))
        data.update(
            filtered_table2(
                name='sent',
                qs=the_prof.profile.sent_by.filter(time_archived__isnull=True),
                filter=SentMessageFilter,
                table=MessageSentTable,
                request=request,
                wrap_list=False,
                self_url=reverse('schooladmin:professor', args=[userid]),
            ))

    return render(request, 'schooladmin/professor.html', data)
