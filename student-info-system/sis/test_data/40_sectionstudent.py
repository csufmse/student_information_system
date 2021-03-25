import os
import sys
from random import randint
import django

sys.path.append(".") # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings") # noqa
django.setup() # noqa

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
    return objs.objects.all()[randint(0, objs.objects.count() - 1)]


i = 0
while i < to_generate:
    i = i + 1

    sec = randobj(Section)

    semstuds = SemesterStudent.objects.filter(semester_id=sec.semester.id)
    if semstuds.count() == 0:
        print(f'No students attend {sec.semester}')
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
        print(f'{i} Unable to put {st} in {sec}')
        i = i - 1
    else:
        print('{} Added {:20} to {} {:15} ({:14},{})'.format(i, str(st), str(sec.semester),
                                                             str(sec), stat, ltr))
