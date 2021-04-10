from datetime import date

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
                        SectionStudent, Profile)
from sis.utils import filtered_table

from .filters import (CourseFilter, MajorFilter, SectionFilter, SectionStudentFilter,
                      SemesterFilter, UserFilter, FullSentMessageFilter,
                      FullReceivedMessageFilter, SentMessageFilter, ReceivedMessageFilter,
                      StudentFilter, ItemFilter, SectionItemFilter)
from .forms import (
    CourseCreationForm,
    CourseEditForm,
    MajorCreationForm,
    MajorEditForm,
    SectionCreationForm,
    SectionEditForm,
    SemesterCreationForm,
    SemesterEditForm,
    ProfessorEditForm,
    ProfessorCreationForm,
)

from sis.forms.profile import DemographicForm, ProfileCreationForm, ProfileEditForm
from sis.forms.user import UserCreationForm, UserEditForm
from sis.forms.student import StudentEditForm, StudentCreationForm
from sis.forms.referenceitem import ReferenceItemCreationForm

from sis.tables.courses import CoursesTable, CoursesForMajorTable, MajorCoursesMetTable
from sis.tables.majors import MajorsTable
from sis.tables.messages import MessageSentTable, MessageReceivedTable
from sis.tables.referenceitems import ProfReferenceItemsTable
from sis.tables.sectionreferenceitems import SectionReferenceItemsTable
from sis.tables.sections import SectionForClassTable, SectionsTable
from sis.tables.sectionstudents import (StudentHistoryTable, SectionStudentsTable,
                                        StudentInSectionTable)
from sis.tables.semesters import SemestersSummaryTable, SemestersTable
from sis.tables.users import UsersTable, FullUsersTable, StudentsTable, StudentInMajorTable


@role_login_required(Profile.ACCESS_ADMIN)
def index(request):
    return render(request, 'schooladmin/home_admin.html')


# USERS


@role_login_required(Profile.ACCESS_ADMIN)
def users(request):
    return render(
        request, 'schooladmin/users.html',
        filtered_table(
            name='users',
            qs=User.annotated(),
            filter=UserFilter,
            table=FullUsersTable,
            request=request,
        ))


@role_login_required(Profile.ACCESS_ADMIN)
def students(request):
    return render(
        request, 'schooladmin/students.html',
        filtered_table(
            name='students',
            qs=User.annotated().filter(profile__role=Profile.ACCESS_STUDENT),
            filter=StudentFilter,
            table=StudentsTable,
            request=request,
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
        filtered_table(
            name='received',
            qs=the_user.profile.sent_to.all(),
            filter=FullReceivedMessageFilter,
            table=MessageReceivedTable,
            request=request,
            wrap_list=False,
        ))
    data.update(
        filtered_table(
            name='sent',
            qs=the_user.profile.sent_by.all(),
            filter=FullSentMessageFilter,
            table=MessageSentTable,
            request=request,
            wrap_list=False,
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
        filtered_table(
            name='semesters',
            qs=the_user.profile.student.semesters.all(),
            filter=SemesterFilter,
            table=SemestersSummaryTable,
            request=request,
            wrap_list=False,
        ))

    data.update(
        filtered_table(
            name='history',
            qs=the_user.profile.student.course_history(),
            filter=SectionStudentFilter,
            table=StudentHistoryTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='remaining',
            qs=the_user.profile.student.remaining_required_courses(),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='majorcourses',
            qs=the_user.profile.student.requirements_met_list(),
            filter=CourseFilter,
            table=MajorCoursesMetTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='received',
            qs=the_user.profile.sent_to.filter(time_archived__isnull=True),
            filter=ReceivedMessageFilter,
            table=MessageReceivedTable,
            request=request,
            wrap_list=False,
        ))
    data.update(
        filtered_table(
            name='sent',
            qs=the_user.profile.sent_by.filter(time_archived__isnull=True),
            filter=SentMessageFilter,
            table=MessageSentTable,
            request=request,
            wrap_list=False,
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
        filtered_table(
            name='semesters',
            qs=the_user.profile.professor.semesters_teaching(),
            filter=SemesterFilter,
            table=SemestersSummaryTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='sections',
            qs=the_user.profile.professor.section_set,
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='items',
            qs=the_user.profile.professor.referenceitem_set,
            filter=ItemFilter,
            table=ProfReferenceItemsTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='received',
            qs=the_user.profile.sent_to.filter(time_archived__isnull=True),
            filter=ReceivedMessageFilter,
            table=MessageReceivedTable,
            request=request,
            wrap_list=False,
        ))
    data.update(
        filtered_table(
            name='sent',
            qs=the_user.profile.sent_by.filter(time_archived__isnull=True),
            filter=SentMessageFilter,
            table=MessageSentTable,
            request=request,
            wrap_list=False,
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
        filtered_table(
            name='items',
            qs=the_user.profile.professor.referenceitem_set,
            filter=ItemFilter,
            table=ProfReferenceItemsTable,
            request=request,
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
        filtered_table(
            name='majors',
            qs=Major.objects,
            filter=MajorFilter,
            table=MajorsTable,
            request=request,
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
        filtered_table(
            name='profs',
            qs=User.annotated().filter(profile__professor__major=the_major),
            filter=UserFilter,
            table=UsersTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='required',
            qs=Course.objects.filter(required_by=the_major),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
        ))

    data.update(
        filtered_table(
            name='offered',
            qs=Course.objects.filter(major=the_major),
            filter=CourseFilter,
            table=CoursesForMajorTable,
            request=request,
        ))

    if include_students:
        data.update(
            filtered_table(
                name='students',
                qs=User.annotated().filter(profile__student__major=the_major),
                filter=UserFilter,
                table=StudentInMajorTable,
                request=request,
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
        filtered_table(
            name='courses',
            qs=Course.objects.all(),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
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
        filtered_table(
            name='sections',
            qs=Section.objects.filter(course=the_course),
            filter=SectionFilter,
            table=SectionForClassTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='prereqs',
            qs=Course.objects.filter(a_prerequisite__course=the_course),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            page_size=5,
        ))
    data.update(
        filtered_table(
            name='neededby',
            qs=Course.objects.filter(a_course__prerequisite=the_course),
            filter=CourseFilter,
            table=CoursesTable,
            request=request,
            page_size=10,
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
        filtered_table(
            name='semesters',
            qs=Semester.objects.all(),
            filter=SemesterFilter,
            table=SemestersTable,
            request=request,
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
        filtered_table(
            name='sections',
            qs=Section.objects.filter(semester=the_semester),
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='students',
            qs=the_semester.students_attending(),
            filter=StudentFilter,
            table=StudentsTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='professors',
            qs=the_semester.professors_teaching(),
            filter=UserFilter,
            table=UsersTable,
            request=request,
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
        filtered_table(
            name='sections',
            qs=Section.objects.all(),
            filter=SectionFilter,
            table=SectionsTable,
            request=request,
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
        filtered_table(
            name='secstud',
            qs=SectionStudent.objects.filter(section=the_section),
            filter=SectionStudentFilter,
            table=StudentInSectionTable,
            request=request,
        ))
    data.update(
        filtered_table(
            name='secitem',
            qs=the_section.sectionreferenceitem_set,
            filter=SectionItemFilter,
            table=SectionReferenceItemsTable,
            request=request,
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

    # if the_user.profile.role == Profile.ACCESS_STUDENT:
    #     return student(request, the_user.id)
    # elif the_user.profile.role == Profile.ACCESS_PROFESSOR:
    #     return professor(request, the_user.id)

    data = {
        'user': the_user,
    }
    data.update(
        filtered_table(
            name='received',
            qs=the_user.profile.sent_to.all(),
            filter=FullReceivedMessageFilter,
            table=MessageReceivedTable,
            request=request,
            wrap_list=False,
        ))
    data.update(
        filtered_table(
            name='sent',
            qs=the_user.profile.sent_by.all(),
            filter=FullSentMessageFilter,
            table=MessageSentTable,
            request=request,
            wrap_list=False,
        ))

    return render(request, 'profile.html', data)


@role_login_required(Profile.ACCESS_ADMIN)
def profile_edit(request):
    return user_edit(request, request.user.id)
