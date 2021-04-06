import os
import sys
from random import choices, choice
import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from sis.models import Section, SectionStudent, SemesterStudent, Student, Semester
from django.db import connection


def createData():
    to_generate = 1000

    statuses = (SectionStudent.REGISTERED, SectionStudent.AWAITING_GRADE, SectionStudent.GRADED,
                SectionStudent.DROP_REQUESTED, SectionStudent.DROPPED)

    grades = (0, 1, 2, 3, 4)
    # no grade inflation here :-/
    choices((0, 1, 2, 3, 4), weights=[2, 2, 4, 4, 5], k=14)

    letter = ('F', 'D', 'C', 'B', 'A')
    sections = Section.objects.all()

    error_count = 0
    i = 0
    while i < to_generate:
        i = i + 1

        sec = choice(sections)

        semstuds = SemesterStudent.objects.filter(semester_id=sec.semester.id)
        if semstuds.count() == 0:
            error_count = error_count + 1
            print(f'WARNING: No students attend {sec.semester}')
            i = i - 1
            continue

        st = choice(semstuds).student

        stat = choices(statuses, weights=[20, 3, 50, 3, 1], k=1)[0]
        g = None
        ltr = '-'
        if stat == 'Graded':
            g = choices(grades, weights=[2, 2, 4, 4, 5], k=1)[0]
            ltr = letter[g]

        ss = SectionStudent(section=sec, student=st, status=stat, grade=g)
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
