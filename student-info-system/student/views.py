from django.shortcuts import redirect, render
from django.http import HttpResponse

from sis.authentication_helpers import role_login_required
from sis.models import Course, Section, Semester, SectionStudent


@role_login_required('Student')
def index(request):
    return redirect('student:current_schedule.html')


@role_login_required('Student')
def current_schedule_view(request):
    context = {'sections': request.user.student.sections.all, 'name': request.user.student.name}
    return render(request, 'student/current_schedule.html', context)


@role_login_required('Student')
def registration_view(request):
    student = request.user.student
    semester_list = student.semesters.order_by('-date_started')
    context = {'student': student, 'semesters': semester_list}
    if semester_list.count() == 0:
        return HttpResponse("You are not registered for any semesters.")

    if request.method == 'POST':
        qs = semester_list.filter(id=request.POST.get('semester'))
        if qs.count() == 1:
            the_sem = qs.get()
            context['semester'] = the_sem.id

            the_sections = the_sem.section_set.all()
            context['sections'] = the_sections
            context['any_sections'] = the_sections.count() != 0

            if request.POST.get('register') is not None:
                any_selected = False

                for s in the_sections:
                    course_val = request.POST.get(str(s.course.id))
                    if course_val is not None and int(course_val) == s.id:
                        status = SectionStudent.REGISTERED
                        if s.seats_remaining < 1:
                            status = SectionStudent.WAITLISTED
                        ss = SectionStudent(section=s, student=student, status=status)
                        ss.save()
                        any_selected = True
                        s.is_selected = True

            # did we complete a registration?
            if any_selected:
                return redirect('student:current_schedule')

    else:
        the_sem = semester_list[0]
        context['semester'] = the_sem.id
        the_sections = the_sem.section_set.all()
        context['sections'] = the_sections
        context['any_sections'] = the_sections.count() != 0

    # signal template that this entry is a different course from last section
    last_course = None
    for s in context['sections']:
        s.new_course = s.course != last_course
        if s.new_course:
            last_course = s.course

    return render(request, 'student/registration.html', context)
