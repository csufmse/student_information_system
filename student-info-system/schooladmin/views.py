from datetime import date, datetime
import pytz
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.urls import reverse

from sis.authentication_helpers import role_login_required

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, Semester, Student,
                        SectionStudent, Profile, Message, Tasks)

from sis.utils import filtered_table, filtered_table2, DUMMY_ID

from sis.filters.course import CourseFilter
from sis.filters.major import MajorFilter
from sis.filters.message import (FullSentMessageFilter, FullReceivedMessageFilter,
                                 SentMessageFilter, ReceivedMessageFilter)
from sis.filters.referenceitem import ItemFilter
from sis.filters.section import SectionFilter
from sis.filters.sectionreferenceitem import SectionItemFilter
from sis.filters.sectionstudent import SectionStudentFilter
from sis.filters.semester import SemesterFilter
from sis.filters.user import StudentFilter, UserFilter

from .forms import (
    CourseCreationForm,
    CourseEditForm,
    SemesterCreationForm,
    SemesterEditForm,
    ProfessorEditForm,
    ProfessorCreationForm,
)

from sis.forms.major import MajorCreationForm, MajorEditForm
from sis.forms.profile import DemographicForm, ProfileCreationForm, ProfileEditForm
from sis.forms.referenceitem import ReferenceItemCreationForm
from sis.forms.section import SectionCreationForm, SectionEditForm
from sis.forms.student import StudentEditForm, StudentCreationForm
from sis.forms.tasks import AcademicProbationTaskForm
from sis.forms.user import UserCreationForm, UserEditForm

from sis.tables.courses import CoursesTable, CoursesForMajorTable, MajorCoursesMetTable
from sis.tables.majors import MajorsTable
from sis.tables.messages import MessageSentTable, MessageReceivedTable
from sis.tables.referenceitems import ProfReferenceItemsTable
from sis.tables.sectionreferenceitems import ReferenceItemsForSectionTable
from sis.tables.sections import SectionForClassTable, SectionsTable
from sis.tables.sectionstudents import (StudentHistoryTable, SectionStudentsTable,
                                        StudentInSectionTable)
from sis.tables.semesters import SemestersSummaryTable, SemestersTable
from sis.tables.users import UsersTable, FullUsersTable, StudentsTable, StudentInMajorTable


@role_login_required(Profile.ACCESS_ADMIN)
def index(request):
    return render(request, 'schooladmin/home_admin.html', request.user.profile.unread_messages())


# USERS


@role_login_required(Profile.ACCESS_ADMIN)
def users(request):
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


@role_login_required(Profile.ACCESS_ADMIN)
def students(request):
    return render(
        request, 'schooladmin/students.html',
        filtered_table2(
            name='students',
            qs=User.objects.all().filter(profile__role=Profile.ACCESS_STUDENT),
            filter=StudentFilter,
            table=StudentsTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:students'),
            click_url=reverse('schooladmin:student', args=[DUMMY_ID]),
        ))


@role_login_required(Profile.ACCESS_ADMIN)
def user(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()
    if request.method == 'POST':
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
        'user': the_user,
    }
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


@role_login_required(Profile.ACCESS_ADMIN)
def student(request, userid):
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
        'user': the_user,
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
            self_url=reverse('schooladmin:student', args=[userid]),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))
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


@role_login_required(Profile.ACCESS_ADMIN)
def professor(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()

    if the_user.profile.role != Profile.ACCESS_PROFESSOR:
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
        'user': the_user,
    }
    data.update(
        filtered_table2(
            name='semesters',
            qs=the_user.profile.professor.semesters_teaching(),
            filter=SemesterFilter,
            table=SemestersSummaryTable,
            request=request,
            self_url=reverse('schooladmin:professor', args=[userid]),
            click_url=reverse('schooladmin:semester', args=[DUMMY_ID]),
        ))

    data.update(
        filtered_table2(
            name='sections',
            qs=the_user.profile.professor.section_set,
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
            self_url=reverse('schooladmin:professor', args=[userid]),
            click_url=reverse('schooladmin:section', args=[DUMMY_ID]),
        ))

    data.update(
        filtered_table2(
            name='items',
            qs=the_user.profile.professor.referenceitem_set,
            filter=ItemFilter,
            table=ProfReferenceItemsTable,
            request=request,
            self_url=reverse('schooladmin:professor', args=[userid]),
            click_url=reverse('schooladmin:professor_item', args=[userid, DUMMY_ID]),
        ))
    data.update(
        filtered_table2(
            name='received',
            qs=the_user.profile.sent_to.filter(time_archived__isnull=True),
            filter=ReceivedMessageFilter,
            table=MessageReceivedTable,
            request=request,
            wrap_list=False,
            self_url=reverse('schooladmin:professor', args=[userid]),
        ))
    data.update(
        filtered_table2(
            name='sent',
            qs=the_user.profile.sent_by.filter(time_archived__isnull=True),
            filter=SentMessageFilter,
            table=MessageSentTable,
            request=request,
            wrap_list=False,
            self_url=reverse('schooladmin:professor', args=[userid]),
        ))

    return render(request, 'schooladmin/professor.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def professor_items(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_user = qs.get()

    if the_user.profile.role != Profile.ACCESS_PROFESSOR:
        return user(request, userid)

    data = {
        'user': the_user,
    }
    data.update(
        filtered_table2(
            name='items',
            qs=the_user.profile.professor.referenceitem_set,
            filter=ItemFilter,
            table=ProfReferenceItemsTable,
            request=request,
            self_url=reverse('schooladmin:professor_items', args=[userid]),
            click_url=reverse('schooladmin:professor_item', args=[userid, DUMMY_ID]),
        ))

    return render(request, 'schooladmin/professor_items.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def professor_item(request, userid, item_id):
    return HttpResponse("not yet")


@role_login_required(Profile.ACCESS_ADMIN)
def professor_item_new(request, userid):
    qs = User.objects.filter(id=userid)
    if qs.count() < 1:
        return HttpResponse("No such user")
    the_prof = qs[0]

    if the_prof.profile.role != Profile.ACCESS_PROFESSOR:
        messages.error(request, "That's not a professor.")
        return user(request, userid)

    if request.method == 'POST':
        form = ReferenceItemCreationForm(request.POST)
        if form.is_valid():
            the_new_item = form.save(commit=False)
            the_new_item.professor = the_prof.profile.professor
            the_new_item.save()
            form.save_m2m()
            messages.success(
                request, f'New item created for ' + f'{the_new_item.course} has been created.')
            return redirect('schooladmin:professor_items', userid=the_prof.id)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        dict = {}
        profs = Professor.objects.filter(profile__user_id=the_prof.id)
        dict['professor'] = profs[0]
        form = ReferenceItemCreationForm(initial=dict)
    return render(request, 'schooladmin/professor_new_item.html', {
        'form': form,
        'user': the_prof
    })


@role_login_required(Profile.ACCESS_ADMIN)
def user_change_password(request, userid):
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
            return redirect('schooladmin:user', userid)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = AdminPasswordChangeForm(request.user)
    return render(request, 'schooladmin/user_change_password.html', {
        'user': the_user,
        'form': form
    })


@transaction.atomic
@role_login_required(Profile.ACCESS_ADMIN)
def user_edit(request, userid):
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
            'user': the_user,
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


# MAJORS


@role_login_required(Profile.ACCESS_ADMIN)
def majors(request):
    return render(
        request, 'schooladmin/majors.html',
        filtered_table2(
            name='majors',
            qs=Major.objects,
            filter=MajorFilter,
            table=MajorsTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:majors'),
            click_url=reverse('schooladmin:major', args=[DUMMY_ID]),
        ))


@login_required
def major(request, majorid):
    include_students = request.user.profile.role in (Profile.ACCESS_ADMIN,
                                                     Profile.ACCESS_PROFESSOR)

    qs = Major.objects.filter(id=majorid)
    if qs.count() < 1:
        return HttpResponse("No such major", reason="Invalid Data", status=404)
    the_major = qs.get()

    data = {
        'major': the_major,
        'permit_edit': request.user.profile.role == Profile.ACCESS_ADMIN,
    }
    data.update(
        filtered_table2(
            name='profs',
            qs=User.objects.all().filter(profile__professor__major=the_major),
            filter=UserFilter,
            table=UsersTable,
            request=request,
            self_url=reverse('schooladmin:major', args=[majorid]),
            click_url=reverse('schooladmin:professor', args=[DUMMY_ID]),
        ))

    data.update(
        filtered_table2(
            name='required',
            qs=Course.objects.filter(required_by=the_major),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            self_url=reverse('schooladmin:major', args=[majorid]),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))

    data.update(
        filtered_table2(
            name='offered',
            qs=Course.objects.filter(major=the_major),
            filter=CourseFilter,
            table=CoursesForMajorTable,
            request=request,
            self_url=reverse('schooladmin:major', args=[majorid]),
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
                self_url=reverse('schooladmin:major', args=[majorid]),
                click_url=reverse('schooladmin:student', args=[DUMMY_ID]),
            ))

    return render(request, 'schooladmin/major.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def major_edit(request, majorid):
    qs = Major.objects.filter(id=majorid)
    if qs.count() < 1:
        return HttpResponse("No such major")
    the_major = qs.get()

    if request.method == 'POST':
        form = MajorEditForm(request.POST, instance=the_major)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            form.save_m2m()
            messages.success(
                request, f'Major {the_major.abbreviation } / {the_major.name} has been updated.')
            return redirect('schooladmin:major', the_major.id)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = MajorEditForm(instance=the_major)
    return render(request, 'schooladmin/major_edit.html', {'major': the_major, 'form': form})


@role_login_required(Profile.ACCESS_ADMIN)
def major_new(request):
    if request.method == 'POST':
        form = MajorCreationForm(request.POST)
        if form.is_valid():
            the_new_major = form.save()
            message = format_html('Major <a href="{}">{} / {}</a> has been created.',
                                  reverse('schooladmin:major', args=[the_new_major.id]),
                                  the_new_major.abbreviation, the_new_major.title)
            messages.success(request, message)
            return redirect('schooladmin:majors')
    else:
        form = MajorCreationForm()
    return render(request, 'schooladmin/major_new.html', {'form': form})


@role_login_required(Profile.ACCESS_ADMIN)
def courses(request):
    return render(
        request, 'schooladmin/courses.html',
        filtered_table2(
            name='courses',
            qs=Course.objects.all(),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:courses'),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))


@role_login_required(Profile.ACCESS_ADMIN)
def course(request, courseid):
    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()

    data = {
        'course': the_course,
    }
    data.update(
        filtered_table2(
            name='sections',
            qs=Section.objects.filter(course=the_course),
            filter=SectionFilter,
            table=SectionForClassTable,
            request=request,
            self_url=reverse('schooladmin:course', args=[courseid]),
            click_url=reverse('schooladmin:section', args=[DUMMY_ID]),
        ))
    data.update(
        filtered_table2(
            name='prereqs',
            qs=Course.objects.filter(a_prerequisite__course=the_course),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            page_size=5,
            self_url=reverse('schooladmin:course', args=[courseid]),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))
    data.update(
        filtered_table2(
            name='neededby',
            qs=Course.objects.filter(a_course__prerequisite=the_course),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            page_size=10,
            self_url=reverse('schooladmin:course', args=[courseid]),
            click_url=reverse('schooladmin:course', args=[DUMMY_ID]),
        ))

    return render(request, 'schooladmin/course.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def course_edit(request, courseid):
    qs = Course.objects.filter(id=courseid)
    if qs.count() < 1:
        return HttpResponse("No such course")
    the_course = qs.get()

    if request.method == 'POST':
        form = CourseEditForm(request.POST, instance=the_course)
        if form.is_valid():
            updated_course = form.save()
            messages.success(request, f'Course {updated_course} successfully updated.')
            return redirect('schooladmin:course', courseid)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = CourseEditForm(instance=the_course)
    return render(request, 'schooladmin/course_edit.html', {'form': form, 'course': the_course})


@role_login_required(Profile.ACCESS_ADMIN)
def course_new(request):
    if request.method == 'POST':
        form = CourseCreationForm(request.POST)
        if form.is_valid():
            the_new_course = form.save()
            messages.success(request, f'Course {the_new_course} has been created.')
            return redirect('schooladmin:courses')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = CourseCreationForm()
    return render(request, 'schooladmin/course_new.html', {'form': form})


@role_login_required(Profile.ACCESS_ADMIN)
def course_section_new(request, courseid):
    return section_new_helper(request, courseid=courseid)


@role_login_required(Profile.ACCESS_ADMIN)
def semesters(request):
    return render(
        request, 'schooladmin/semesters.html',
        filtered_table2(
            name='semesters',
            qs=Semester.objects.all(),
            filter=SemesterFilter,
            table=SemestersTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:semesters'),
            click_url=reverse('schooladmin:semester', args=[DUMMY_ID]),
        ))


@role_login_required(Profile.ACCESS_ADMIN)
def semester(request, semester_id):
    qs = Semester.objects.filter(id=semester_id)
    if qs.count() < 1:
        return HttpResponse("No such semester")
    the_semester = qs.get()

    data = {
        'semester': the_semester,
    }
    data.update(
        filtered_table2(
            name='sections',
            qs=Section.objects.filter(semester=the_semester),
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
            self_url=reverse('schooladmin:semester', args=[semester_id]),
            click_url=reverse('schooladmin:section', args=[DUMMY_ID]),
        ))
    data.update(
        filtered_table2(
            name='students',
            qs=the_semester.students_attending(),
            filter=StudentFilter,
            table=StudentsTable,
            request=request,
            self_url=reverse('schooladmin:semester', args=[semester_id]),
            click_url=reverse('schooladmin:student', args=[DUMMY_ID]),
        ))
    data.update(
        filtered_table2(
            name='professors',
            qs=the_semester.professors_teaching(),
            filter=UserFilter,
            table=UsersTable,
            request=request,
            self_url=reverse('schooladmin:semester', args=[semester_id]),
            click_url=reverse('schooladmin:professor', args=[DUMMY_ID]),
        ))

    return render(request, 'schooladmin/semester.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def semester_edit(request, semester_id):
    qs = Semester.objects.filter(id=semester_id)
    if qs.count() < 1:
        return HttpResponse("No such semester")
    the_semester = qs.get()

    if request.method == 'POST':
        form = SemesterEditForm(request.POST, instance=the_semester)
        if form.is_valid():
            the_updated_sem = form.save()
            messages.success(request, f'Semester {the_updated_sem} has been updated.')
            return redirect('schooladmin:semester', semester_id)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = SemesterEditForm(instance=the_semester)
    return render(request, 'schooladmin/semester_edit.html', {
        'form': form,
        'semester': the_semester
    })


@role_login_required(Profile.ACCESS_ADMIN)
def semester_new(request):
    if request.method == 'POST':
        form = SemesterCreationForm(request.POST)
        if form.is_valid():
            try:
                the_new_semester = form.save()
                messages.success(request, f'Semester {the_new_semester} has been created.')
                return redirect('schooladmin:semesters')
            except Exception:
                messages.error(request,
                               'Semester is a duplicate of an existing one. Please correct.')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = SemesterCreationForm(initial={
            'year': date.today().year,
        })
    return render(request, 'schooladmin/semester_new.html', {'form': form})


@role_login_required(Profile.ACCESS_ADMIN)
def semester_section_new(request, semester_id):
    return section_new_helper(request, semester_id=semester_id)


@role_login_required(Profile.ACCESS_ADMIN)
def sections(request):
    return render(
        request, 'schooladmin/sections.html',
        filtered_table2(
            name='sections',
            qs=Section.objects.all(),
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
            scrollable=True,
            self_url=reverse('schooladmin:sections'),
            click_url=reverse('schooladmin:section', args=[DUMMY_ID]),
        ))


@role_login_required(Profile.ACCESS_ADMIN)
def section(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    data = {
        'section': the_section,
    }
    data.update(
        filtered_table2(
            name='secstuds',
            qs=SectionStudent.objects.filter(section=the_section),
            filter=SectionStudentFilter,
            table=StudentInSectionTable,
            request=request,
            self_url=reverse('schooladmin:section', args=[sectionid]),
            click_url=reverse('schooladmin:sectionstudent', args=[DUMMY_ID]),
        ))
    data.update(
        filtered_table2(
            name='secitems',
            qs=the_section.sectionreferenceitem_set,
            filter=SectionItemFilter,
            table=ReferenceItemsForSectionTable,
            request=request,
            self_url=reverse('schooladmin:section', args=[sectionid]),
        ))

    return render(request, 'schooladmin/section.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def section_refreshitems(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    the_section.refresh_reference_items()

    messages.success(request, "Items refreshed for section")
    return redirect('schooladmin:section', sectionid)


@role_login_required(Profile.ACCESS_ADMIN)
def section_students_manage(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    return HttpResponse('not implemented yet')


@role_login_required(Profile.ACCESS_ADMIN)
def section_edit(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()

    if request.method == 'POST':
        form = SectionEditForm(request.POST, instance=the_section)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            form.save_m2m()
            obj.refresh_reference_items()
            messages.success(request, f'Section {obj} has been updated.')
            return redirect('schooladmin:section', sectionid)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = SectionEditForm(instance=the_section)
    return render(request, 'schooladmin/section_edit.html', {
        'form': form,
        'section': the_section
    })


@role_login_required(Profile.ACCESS_ADMIN)
def section_new_from_section(request, sectionid):
    qs = Section.objects.filter(id=sectionid)
    if qs.count() < 1:
        return HttpResponse("No such section")
    the_section = qs.get()
    return section_new_helper(request,
                              courseid=the_section.course.id,
                              semester_id=the_section.semester.id)


@role_login_required(Profile.ACCESS_ADMIN)
def section_new(request):
    return section_new_helper(request)


def section_new_helper(request, semester_id=None, courseid=None):
    if request.method == 'POST':
        form = SectionCreationForm(request.POST)
        if form.is_valid():
            the_course = form.cleaned_data['course']
            the_sem = form.cleaned_data['semester']
            current_max_section = the_course.max_section_for_semester(the_sem)
            if current_max_section is None:
                next_section = 1
            else:
                next_section = current_max_section + 1
            the_new_section = form.save(commit=False)
            the_new_section.number = next_section
            the_new_section.save()
            the_new_section.refresh_reference_items()
            messages.success(request, f'Section {the_new_section} has been created.')
            return redirect('schooladmin:section', the_new_section.id)
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form_values = {}
        if courseid is not None:
            qs = Course.objects.filter(id=courseid)
            if qs.count() < 1:
                return HttpResponse("No such course")
            the_course = qs.get()

            form_values['course'] = the_course

        if semester_id is not None:
            qs = Semester.objects.filter(id=semester_id)
            if qs.count() < 1:
                return HttpResponse("No such semester")
            the_semester = qs.get()
            form_values['semester'] = the_semester
        else:
            semesters = Semester.objects.order_by('-date_registration_opens').filter(
                date_registration_opens__lte=date.today(), date_last_drop__gte=date.today())
            if semesters.count() > 0:
                form_values['semester'] = semesters[0]

        form = SectionCreationForm(initial=form_values)
    return render(
        request, 'schooladmin/section_new.html', {
            'profs': Professor.objects.filter(profile__user__is_active=True),
            'courses': Course.objects.all(),
            'form': form,
        })


@role_login_required(Profile.ACCESS_ADMIN)
def sectionstudent(request, id):
    qs = SectionStudent.objects.filter(id=id)
    if qs.count() < 1:
        return HttpResponse("No such sectionstudent")
    the_sectionstud = qs.get()

    return HttpResponse('not implemented yet')


@role_login_required(Profile.ACCESS_ADMIN)
def transcript(request, userid):
    student = Student.objects.get(profile__user__id=userid)
    data = {'student': student}
    ssects = student.sectionstudent_set.all().order_by('section__semester')
    if len(ssects):
        ssects_by_sem = [[ssects[0]]]
        i = 0
        for ssect in ssects:
            if ssect.section.semester == ssects_by_sem[i][0].section.semester:
                ssects_by_sem[i].append(ssect)
            else:
                i += 1
                ssects_by_sem.insert(i, [ssect])
        data['ssects_by_sem'] = ssects_by_sem
    return render(request, 'schooladmin/transcript.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def demographics(request):
    students = Profile.demographics_for(Profile.objects.filter(role=Profile.ACCESS_STUDENT))
    professors = Profile.demographics_for(Profile.objects.filter(role=Profile.ACCESS_PROFESSOR))

    # FORMAT RESULTS
    stud_form = [{'key': 'Total Students', 'data': '', 'total': students['count']}]
    del students['count']
    for attr in Profile.DEMO_ATTRIBUTE_MAP:
        attrdata = students[attr[2]]
        total = 0
        line = ''
        for item in attrdata.items():
            line += f', {item[0]} = {item[1]}'
            total += item[1]
        line = line[2:]
        stud_form.append({'key': attr[2], 'data': line, 'total': total})

    prof_form = [{'key': 'Total Professors', 'data': '', 'total': professors['count']}]
    del professors['count']
    for attr in Profile.DEMO_ATTRIBUTE_MAP:
        attrdata = professors[attr[2]]
        total = 0
        line = ''
        for item in attrdata.items():
            line += f', {item[0]} = {item[1]}'
            total += item[1]
        line = line[2:]
        prof_form.append({'key': attr[2], 'data': line, 'total': total})

    return render(request, 'schooladmin/demographics.html', {
        'students': stud_form,
        'professors': prof_form,
    })


@role_login_required(Profile.ACCESS_ADMIN)
def profile(request):
    the_user = request.user

    data = {
        'user': the_user,
    }
    data.update(
        filtered_table2(
            name='received',
            qs=the_user.profile.sent_to.all(),
            filter=FullReceivedMessageFilter,
            table=MessageReceivedTable,
            request=request,
            wrap_list=False,
            self_url=reverse('schooladmin:profile'),
        ))
    data.update(
        filtered_table2(
            name='sent',
            qs=the_user.profile.sent_by.all(),
            filter=FullSentMessageFilter,
            table=MessageSentTable,
            request=request,
            wrap_list=False,
            self_url=reverse('schooladmin:profile'),
        ))

    return render(request, 'schooladmin/profile.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def profile_edit(request):
    return user_edit(request, request.user.id)


@role_login_required(Profile.ACCESS_ADMIN)
def usermessages(request):
    the_user = request.user

    sentFilter = FullSentMessageFilter
    receivedFilter = FullReceivedMessageFilter
    if the_user.profile.role == Profile.ACCESS_STUDENT:
        sentFilter = SentMessageFilter
        receivedFilter = ReceivedMessageFilter

    data = {
        'user': the_user,
    }
    data.update(
        filtered_table(
            name='received',
            qs=the_user.profile.sent_to.all(),
            filter=receivedFilter,
            table=MessageReceivedTable,
            request=request,
            wrap_list=False,
        ))
    data.update(
        filtered_table(
            name='sent',
            qs=the_user.profile.sent_by.all(),
            filter=sentFilter,
            table=MessageSentTable,
            request=request,
            wrap_list=False,
        ))

    return render(request, 'schooladmin/messages.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def message(request, id):
    the_user = request.user
    the_profile = the_user.profile
    the_mess = Message.objects.get(id=id)
    is_recipient = the_mess.recipient == the_profile
    is_sender = the_mess.sender == the_profile
    is_student = the_profile.role == Profile.ACCESS_STUDENT

    if the_mess is None:
        messages.error(request, 'Invalid message')
        return redirect('schooladmin:messages')

    if not (is_sender or is_recipient) and the_profile != Profile.ACCESS_ADMIN:
        messages.error(request, 'Invalid message')

    if request.method == 'POST':
        if request.POST.get('unarchive', None) is not None:
            messages.success(request, 'Message unarchived.')
            the_mess.time_archived = None
            the_mess.save()

        elif request.POST.get('archive', None) is not None:
            messages.success(request, 'Message archived.')
            the_mess.time_archived = datetime.now(pytz.utc)
            the_mess.save()

        elif request.POST.get('reply', None) is not None:
            messages.success(request, 'Trust me, you replied.')

        elif request.POST.get('approvedrop', None) is not None:
            the_student = Student.objects.get(id=the_mess.support_data['student'])
            the_ssect = SectionStudent.objects.get(id=the_mess.support_data['section'])
            the_student.drop_approved(sectionstudent=the_ssect, request_message=the_mess)
            messages.success(request, 'Drop Approved.')

        elif request.POST.get('rejectdrop', None) is not None:
            the_mess.time_handled = datetime.now(pytz.utc)
            the_mess.save()
            messages.success(request, 'Trust me, you rejected the drop.')

        elif request.POST.get('approvemajor', None) is not None:
            the_student = Student.objects.get(id=the_mess.support_data['student'])
            the_new_major = Major.objects.get(id=the_mess.support_data['major'])
            the_student.major_change_approved(major=the_new_major, request_message=the_mess)
            messages.success(request, 'Major Change Approved.')

        elif request.POST.get('rejectmajor', None) is not None:
            the_mess.time_handled = datetime.now(pytz.utc)
            the_mess.save()
            messages.success(request, 'Trust me, you rejected the major change.')

        else:
            messages.error(request, 'Something went wrong.')

    # mark our received messages read. Don't touch sent messages.
    if is_recipient and the_mess.time_read is None:
        the_mess.time_read = datetime.now(pytz.utc)
        the_mess.save()

    handled = the_mess.time_handled is not None
    handleable_message = the_mess.message_type in (Message.DROP_REQUEST_TYPE,
                                                   Message.MAJOR_CHANGE_TYPE)
    show_drop = is_recipient and the_mess.message_type == Message.DROP_REQUEST_TYPE \
        and not handled
    show_major = is_recipient and the_mess.message_type == Message.MAJOR_CHANGE_TYPE \
        and not handled
    return render(
        request, 'schooladmin/message.html', {
            'user': the_user,
            'message': the_mess,
            'show_approve_drop': show_drop,
            'show_approve_major': show_major,
            'show_archive': is_recipient,
            'message_archived': the_mess.time_archived is not None,
            'message_read': the_mess.time_read is not None,
            'message_handled': handled,
            'show_type': not is_student,
            'show_handled': handleable_message and not is_student,
            'show_read': True,
        })


@role_login_required(Profile.ACCESS_ADMIN)
def tasks(request):
    tasks = Tasks.objects.all()
    data = [x.task for x in tasks]
    return render(request, 'schooladmin/tasks.html', {'data': data})


@role_login_required(Profile.ACCESS_ADMIN)
def task_add(request):
    if request.method == 'POST':
        form = AcademicProbationTaskForm(request.Post)
        try:
            task = form.save()
            messages.success(request, 'Successfully created a task')
        except ValueError as e:
            messages.error(request, 'Something in the form is incorrect, see errors')
            return render(request, 'schooladmin/task_add.html', {'form': form})
        Tasks.add_task(task)
    else:
        form = AcademicProbationTaskForm()
    return render(request, 'schooladmin/task_add.html', {'form': form})

@role_login_required(Profile.ACCESS_ADMIN)
def task_edit(request, task_id):
   pass 
