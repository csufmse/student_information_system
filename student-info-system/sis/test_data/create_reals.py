import os
import sys
from random import randint, choice, shuffle, random, choices, randrange
from datetime import datetime

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from sis.models import *
from django.db import connection

capacities = (10,) * 3 + (30,) * 11 + (100,) * 3

durations = (30,) * 7 + (60,) * 6 + (90,) * 3 + (180,) * 3

days = ('M', 'T', 'W', 'Th', 'F', 'Sa', 'Su')


def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))


def diff(li1, li2):
    return (list(list(set(li1) - set(li2)) + list(set(li2) - set(li1))))


def choose_days():
    d = ''
    max = 1 << len(days)

    my_days = randint(1, max - 1)

    for bit in range(0, 8):
        if my_days & (1 << bit):
            d = d + days[bit]

    return d


def choose_hours():
    # 0700 + up to 12 hours (24 * 30 min)
    start = 420 + 30 * randint(0, 24 - 1)
    dur = choice(durations)

    h = '{:02d}{:02d}-{:02d}{:02d}'.format(int(start / 60), int(start % 60), int((start) / 60),
                                           int((start + dur) % 60))
    return h


def set_up_sectionstudent(secstud):
    sec = secstud.section
    if sec.status == Section.REG_CLOSED:
        if random() < 0.05:
            if random() < 0.75:
                secstud.status = SectionStudent.DROPPED
            else:
                secstud.status = SectionStudent.DROP_REQUESTED
        else:
            secstud.status = SectionStudent.REGISTERED
    elif sec.status == Section.REG_OPEN:
        if random() < 0.1:
            if random() < 0.75:
                secstud.status = SectionStudent.DROPPED
            else:
                secstud.status = SectionStudent.DROP_REQUESTED
        else:
            secstud.status = SectionStudent.REGISTERED
    elif sec.status == Section.IN_PROGRESS:
        secstud.status = SectionStudent.IN_PROGRESS
    elif sec.status == Section.GRADING:
        if random() < 0.3:
            secstud.status = SectionStudent.AWAITING_GRADE
        else:
            secstud.status = SectionStudent.GRADED
            g = choices((0, 1, 2, 3, 4), weights=[1, 1, 3, 4, 5], k=1)[0]
            secstud.grade = g
    elif sec.status == Section.GRADED:
        secstud.status = SectionStudent.GRADED
        g = choices((0, 1, 2, 3, 4), weights=[1, 1, 3, 4, 5], k=1)[0]
        secstud.grade = g
    elif sec.status == Section.CANCELLED:
        secstud.status = SectionStudent.DROPPED


def createData():

    courses = list(Course.objects.all())
    shuffle(courses)
    letter = ('F', 'D', 'C', 'B', 'A')

    max_number_of_courses_to_create = 3 * Professor.objects.count()

    semesters = Semester.objects.order_by('date_started')
    error_count = 0

    for sem in semesters:
        print(f'*** BEGINNING {sem} ***')
        semstudents = sem.semesterstudent_set.all()

        needed = {}
        majors = []
        for semstud in semstudents:
            for course in semstud.student.remaining_required_courses(deep=True):
                if course.major not in majors:
                    majors.append(course.major)
                if course not in needed:
                    needed[course] = 0
                needed[course] += 1
        most_needed = sorted(needed.keys(), reverse=True, key=lambda c: needed[c])

        # creating less than actually needed
        number_of_courses_to_create = min(max_number_of_courses_to_create,
                                          int(len(most_needed) * 0.75))

        print(f'{len(most_needed)} courses needed by {len(semstudents)} students. ', end='')
        if len(semstudents):
            print(f'Course {most_needed[0]} needed by {needed[most_needed[0]]} students')

        # fill out schedule with other courses
        not_needed = diff(courses, most_needed)
        shuffle(not_needed)
        to_schedule = (most_needed + not_needed)[0:number_of_courses_to_create]

        print(f'Creating {len(to_schedule)} sections')

        print(f'*** BEGINNING sections ***')
        sections = []
        for c in to_schedule:
            ps = Professor.objects.filter(major=c.major)
            # if ps.count() == 0:
            #     print(f'ERROR: No teachers for {c} ...')
            #     error_count = error_count + 1
            #     continue

            p = choice(ps)
            d = choose_days()
            h = choose_hours()
            cap = choice(capacities)

            if sem.registration_open():
                if random() < 0.1:
                    stat = Section.REG_CLOSED
                elif random() < 0.1:
                    stat = Section.CANCELLED
                else:
                    stat = Section.REG_OPEN
            elif sem.in_session():
                stat = Section.IN_PROGRESS
            elif sem.preparing_grades():
                stat = Section.GRADING
            else:
                stat = Section.GRADED

            max_section = c.max_section_for_semester(semester=sem)
            n = max_section + 1

            s = Section(course=c,
                        professor=p,
                        semester=sem,
                        number=n,
                        capacity=cap,
                        location='somewhere',
                        hours=d + h,
                        status=stat)
            try:
                s.save()
            except Exception:
                error_count = error_count + 1
                print(f'ERROR: Unable to create sec {n} for {c}')
            else:
                print('Created sec {} for {:15} in {} ({})'.format(str(n), str(c), str(sem),
                                                                   stat))
                sections.append(s)

        print(f'*** BEGINNING STUDENTS ***')
        for semstud in semstudents:

            # now schedule students for it
            number_attended = randrange(3, 6)

            print(
                f'{semstud.student} ({semstud.student.major.abbreviation}) reg ' +
                f'for {number_attended} sections: ',
                end='')

            # start by listing the ones for whom we've met the requirements
            prereqs_met = [
                aSec for aSec in sections if aSec.course.prerequisites_met(semstud.student)
            ]
            print(f'prereqs_met={len(prereqs_met)}, ', end='')

            if len(prereqs_met) == 0:
                print(f'ERROR: Student {semstud.student} meets the prereqs for NO ' +
                      f'classes in semester {sem}')
                continue

            elif len(prereqs_met) < number_attended:
                print(f'WARNING: Student {semstud.student} wants to attend {number_attended} ' +
                      f'courses but only meets the prereqs for {len(prereqs_met)}.')
                number_attended = len(prereqs_met)

            # don't take classes twice
            courses_passed = [
                aSec.section.course for aSec in semstud.student.course_history(passed=True)
            ]

            original_len = len(prereqs_met)
            for aSec in prereqs_met:
                if aSec.course in courses_passed:
                    prereqs_met.remove(aSec)

            print(f'removed[passed]={original_len-len(prereqs_met)}, ', end='')

            # all required courses
            deep_requirements = Course.deep_prerequisites_for(
                semstud.student.major.courses_required.all(), include_self=True)

            print(f'deep_req={len(deep_requirements)}, ', end='')

            # sections that meet a requirement
            reqd_secs = []
            for sec in prereqs_met:
                if sec.course in deep_requirements:
                    reqd_secs.append(sec)

            print(f'deep_secs={len(reqd_secs)}, ', end='')

            # take as many as we can
            attending = reqd_secs[0:number_attended]

            if number_attended > len(attending):
                # but if there weren't enough, take the others
                extras = diff(prereqs_met, reqd_secs)

                print(f'extras={len(extras)}, ', end='')

                # bias towards their major
                weights = list(
                    map((lambda sec: 10 if sec.course.major == semstud.student.major else 1),
                        extras))

                potentials = diff(extras, attending)
                if len(potentials) < number_attended - len(attending):
                    attending.extend(potentials)
                else:
                    while len(attending) < number_attended:
                        aSec = choices(extras, weights=weights, k=1)[0]
                        if aSec not in attending:
                            attending.append(aSec)

            print(f'attending={len(attending)}')

            sec_index = 0
            while sec_index < len(attending):
                sec = attending[sec_index]
                sec_index = sec_index + 1

                secstud = None
                try:
                    secstud = sec.register(student=semstud.student, check_section_status=False)
                except NoSeatsRemaining:
                    newsec = sec.open_new_section_from()
                    if newsec.status != Section.REG_CLOSED:
                        newsec.status = sec.status
                        newsec.save()
                    sections.append(newsec)
                    sec = newsec
                    Message.objects.create(sender=sec.course.major.contact,
                                           recipient=sec.course.major.contact,
                                           message_type=Message.SECTION_ADDED,
                                           subject=f'Created section {sec} ({sem})',
                                           support_data={'section': sec.pk})

                    print(f'Opened new section {sec} in {sem}')
                    secstud = sec.register(student=semstud.student, check_section_status=False)

                set_up_sectionstudent(secstud)

                if secstud.grade is None:
                    ltr = '-'
                else:
                    ltr = letter[secstud.grade]

                try:
                    secstud.save()
                except Exception:
                    error_count = error_count + 1
                    print(f'ERROR: Unable to put {secstud.student} in {sec} [sec={sec.id}, ' +
                          f'stud={secstud.student.profile.user.id}, ' + f'grade={ltr}]')
                    print(f'attending = {attending}')
                else:
                    reqd = "REQD" if sec.course in deep_requirements else ""
                    print('Added {:20} to {} {:15} ({:14},{}) {}'.format(
                        str(secstud.student), str(sec.semester), str(sec), secstud.status, ltr,
                        reqd))

        print(f'*** BEGINNING SECTION CLEANUP ***')
        for sec in sections:
            if sec.students.count() == 0 and random() < 0.7:
                print(f'Deleting {sec}')
                sec.delete()


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_section')


if __name__ == "__main__":
    createData()
