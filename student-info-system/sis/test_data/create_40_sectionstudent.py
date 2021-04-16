import os
import sys
from random import choices, choice, shuffle, random, randrange, randint
import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from sis.models import Section, SectionStudent, SemesterStudent, Student, Semester, Course
from django.db import connection


def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))


def diff(li1, li2):
    return (list(list(set(li1) - set(li2)) + list(set(li2) - set(li1))))


def createData():
    to_generate = 4 * SemesterStudent.objects.all().count()

    letter = ('F', 'D', 'C', 'B', 'A')

    error_count = 0

    i = 0
    for sem in Semester.objects.order_by('date_started').all():
        if i > to_generate:
            break

        semstuds = SemesterStudent.objects.filter(semester=sem)
        if semstuds.count() == 0:
            print(f'WARNING: No students attend {sem}')
            continue

        number_attended = randrange(3, 6)
        sections = list(Section.objects.filter(semester=sem))

        for semstud in semstuds:

            # start by listing the ones for whom we've met the requirements
            prereqs_met = [
                aSec for aSec in sections if aSec.course.prerequisites_met(semstud.student)
            ]
            print(f'{semstud}: prereqs_met={len(prereqs_met)}, ', end='')

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
                semstud.student.major.courses_required.all())

            print(f'deep_req={len(deep_requirements)}, ', end='')

            # sections that meet a requirement
            reqd_secs = []
            for sec in prereqs_met:
                if sec.course in deep_requirements:
                    reqd_secs.append(sec)

            print(f'deep_secs={len(reqd_secs)}, ', end='')

            # take as many as we can
            attending = reqd_secs[0:number_attended]

            # but if there weren't enough, take the others
            extras = diff(prereqs_met, reqd_secs)

            print(f'extras={len(extras)}, ', end='')

            # bias towards their major
            weights = list(
                map((lambda sec: 10 if sec.course.major == semstud.student.major else 1), extras))

            while len(attending) < number_attended:
                aSec = choices(extras, weights=weights, k=1)[0]
                if aSec.seats_remaining and not (aSec in attending):
                    attending.append(aSec)

            print(f'attending={len(attending)}')

            for sec in attending:
                try:
                    ss = sec.register(student=semstud.student)

                    if sec.status == Section.REG_CLOSED:
                        if random() < 0.05:
                            if random() < 0.75:
                                ss.status = SectionStudent.DROPPED
                            else:
                                ss.status = SectionStudent.DROP_REQUESTED
                        else:
                            ss.status = SectionStudent.REGISTERED
                    elif sec.status == Section.REG_OPEN:
                        if random() < 0.1:
                            if random() < 0.75:
                                ss.status = SectionStudent.DROPPED
                            else:
                                ss.status = SectionStudent.DROP_REQUESTED
                        else:
                            ss.status = SectionStudent.REGISTERED
                    elif sec.status == Section.IN_PROGRESS:
                        ss.status = SectionStudent.IN_PROGRESS
                    elif sec.status == Section.GRADING:
                        if random() < 0.3:
                            ss.status = SectionStudent.AWAITING_GRADE
                        else:
                            ss.status = SectionStudent.GRADED
                            g = choices((0, 1, 2, 3, 4), weights=[1, 1, 3, 4, 5], k=1)[0]
                            ss.grade = g
                    elif sec.status == Section.GRADED:
                        ss.status = SectionStudent.GRADED
                        g = choices((0, 1, 2, 3, 4), weights=[1, 1, 3, 4, 5], k=1)[0]
                        ss.grade = g
                    elif sec.status == Section.CANCELLED:
                        ss.status = SectionStudent.DROPPED

                    if ss.grade is None:
                        ltr = '-'
                    else:
                        ltr = letter[ss.grade]

                    ss.save()
                except Exception:
                    error_count = error_count + 1
                    print(f'ERROR: {i} Unable to put {semstud.student} in {sec} [sec={sec.id}, ' +
                          f'stud={semstud.student.profile.user.id}, ' +
                          f'status={ss.status}, grade={ltr}]')
                    print(f'attending = {attending}')
                    i = i - 1
                else:
                    reqd = "REQD" if sec.course in deep_requirements else ""
                    print('{} Added {:20} to {} {:15} ({:14},{}) {}'.format(
                        i, str(semstud.student), str(sec.semester), str(sec), ss.status, ltr,
                        reqd))
                i = i + 1
    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_sectionstudent')


if __name__ == "__main__":
    createData()
