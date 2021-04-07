import os
import sys
from random import choices, choice, shuffle, random, randrange, randint
import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from sis.models import Section, SectionStudent, SemesterStudent, Student, Semester
from django.db import connection
from datetime import datetime

def createData():
    to_generate = 1000

    statuses = (SectionStudent.REGISTERED, SectionStudent.AWAITING_GRADE, SectionStudent.GRADED,
                SectionStudent.DROP_REQUESTED, SectionStudent.DROPPED)

    grades = (0, 1, 2, 3, 4)
    # no grade inflation here :-/
    choices((0, 1, 2, 3, 4), weights=[2, 2, 4, 4, 5], k=14)

    letter = ('F', 'D', 'C', 'B', 'A')
    sections = list(Section.objects.all())

    error_count = 0
    now = datetime.now()

    for sem in Semester.objects.all():
        semstuds = SemesterStudent.objects.filter(semester=sem)
        if semstuds.count() == 0:
            print(f'WARNING: No students attend {sem}')
            continue

        number_attended = randrange(1,6)
        sections = list(Section.objects.filter(semester=sem))
        for semstud in semstuds:
            shuffle(sections)

            for sec in sections[0:number_attended]:
                ss = SectionStudent(section=sec, student=semstud.student)
                if sec.status == Section.CLOSED:
                    continue
                elif sec.status == Section.OPEN:
                    if random() < 0.1:
                        if random() < 0.75:
                            ss.status = SectionStudent.DROPPED
                        else:
                            ss.status = SectionStudent.DROP_REQUESTED
                    else:
                        ss.status = SectionStudent.REGISTERED
                elif sec.status == Section.IN_PROGRESS:
                    ss.status = SectionStudent.AWAITING_GRADE
                elif sec.status == Section.GRADING:
                    ss.status = SectionStudent.AWAITING_GRADE
                elif sec.status == Section.GRADED:
                    ss.status = SectionStudent.GRADED
                    g = choices(grades, weights=[2, 2, 4, 4, 5], k=1)[0]
                    ltr = letter[g]
                    ss.grade = g
                elif sec.status == Section.CANCELLED:
                    ss.status = SectionStudent.DROPPED
        st = choice(semstuds).student

        stat = choices(statuses, weights=[20, 3, 50, 3, 1], k=1)[0]
        g = None
        ltr = '-'
        if stat == 'Graded':
            g = choices(grades, weights=[2, 2, 4, 4, 5], k=1)[0]
            ltr = letter[g]

        try:
            ss.save()
        except Exception:
            error_count = error_count + 1
            print(
                f'ERROR: {i} Unable to put {st} in {sec} [sec={sec.id}, ' +
                f'stud={st.profile.user.id}, status={stat}, grade={g}]')
            i = i - 1
        else:
            print('{} Added {:20} to {} {:15} ({:14},{})'.format(i, str(st), str(sec.semester),
                                                                 str(sec), stat, ltr))
    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_sectionstudent')


if __name__ == "__main__":
    createData()
