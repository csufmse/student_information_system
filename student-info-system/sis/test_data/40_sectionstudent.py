import os
import sys
from random import randint
import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from sis.models import Section, SectionStudent, SemesterStudent, Student

to_generate = 1000

statuses = (SectionStudent.REGISTERED,) * 20 + \
        (SectionStudent.AWAITING_GRADE,) * 3 + \
        (SectionStudent.GRADED,) * 50 + \
        (SectionStudent.DROP_REQUESTED,) * 3 + \
        (SectionStudent.DROPPED,) * 1

# no grade inflation here :-/
grades = (0,) * 2 + (1,) * 2 + (2,) * 4 + (3,) * 4 + (4,) * 5

letter = ('F', 'D', 'C', 'B', 'A')


def randobj(objs):
    ii = randint(0, objs.objects.count() - 1)
    obj = None
    try:
        obj = objs.objects.all()[ii]
    except Exception:
        print(f'could not get ix {ii} of {objs}, count {objs.objects.count()-1}')
    return obj


error_count = 0
i = 0
while i < to_generate:
    i = i + 1

    while True:
        sec = randobj(Section)
        if sec is not None:
            break

    semstuds = SemesterStudent.objects.filter(semester_id=sec.semester.id)
    if semstuds.count() == 0:
        error_count = error_count + 1
        print(f'WARNING: No students attend {sec.semester}')
        i = i - 1
        continue

    st = semstuds[randint(0, semstuds.count() - 1)].student

    stat = statuses[randint(0, len(statuses) - 1)]
    g = None
    ltr = '-'
    if stat == 'Graded':
        g = grades[randint(0, len(grades) - 1)]
        ltr = letter[g]

    ss = SectionStudent(section=sec, student=st, status=stat, grade=g)
    try:
        ss.save()
    except Exception:
        error_count = error_count + 1
        print(f'ERROR: {i} Unable to put {st} in {sec} [sec={sec.id}, stud={st.user_id}, ' +
              f'status={stat}, grade={g}]')
        i = i - 1
    else:
        print('{} Added {:20} to {} {:15} ({:14},{})'.format(i, str(st), str(sec.semester),
                                                             str(sec), stat, ltr))
if error_count:
    print(f'ERROR: {error_count} errors occurred')
