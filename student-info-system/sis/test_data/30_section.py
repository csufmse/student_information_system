import os
import sys
from random import randint

import django
from sis.models import Course, Major, Professor, Section, Semester

sys.path.append(".")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# set low to generate multiple sections per semester, count() to spread
# them across all courses
# course_max = 10
course_max = Course.objects.count()

# concentrate on how many of the latest sections?
# sem_count = 1
sem_count = Semester.objects.count()

to_generate = 500

capacities = (10,) * 3 + (30,) * 11 + (100,) * 3

durations = (30,) * 7 + (60,) * 6 + (90,) * 3 + (180,) * 3

days = ('M', 'T', 'W', 'Th', 'F', 'Sa', 'Su')

statuses = (Section.CLOSED,) * 3 + \
            (Section.OPEN,) * 10 + \
            (Section.IN_PROGRESS,) * 10 + \
            (Section.GRADING,) * 5 + \
            (Section.GRADED,) * 30 + \
            (Section.CANCELLED,) * 3


def choose_days():
    d = ''
    max = 1 << len(days)

    my_days = randint(1, max - 1)

    for bit in range(0, 8):
        if my_days & (1 << bit):
            d = d + days[bit]

    return d


def choose_hours():
    # 0700 + up to 12 hours
    start = 420 + 30 * randint(0, 24 - 1)
    dur = durations[randint(0, len(durations) - 1)]

    h = '{:02d}{:02d}-{:02d}{:02d}'.format(int(start / 60), int(start % 60), int((start) / 60),
                                           int((start + dur) % 60))
    return h


def randobj(objs):
    return objs.objects.all()[randint(0, objs.objects.count() - 1)]


i = 0
while i < to_generate:
    i = i + 1

    c = Course.objects.order_by('id')[randint(0, course_max - 1)]

    ps = Professor.objects.filter(major=c.major)
    if ps.count() == 0:
        print(f'No teachers for {c} ...')
        i = i - 1
        continue

    p = ps[randint(0, ps.count() - 1)]
    sem = Semester.objects.all().order_by('-date_started')[randint(0, sem_count - 1)]
    d = choose_days()
    h = choose_hours()
    cap = capacities[randint(0, len(capacities) - 1)]

    number_of_sections = Section.objects.filter(course=c, semester=sem).count()
    n = number_of_sections + 1

    stat = statuses[randint(0, len(statuses) - 1)]

    s = Section(course=c,
                professor=p,
                semester=sem,
                number=n,
                capacity=cap,
                hours=d + h,
                status=stat)
    try:
        s.save()
    except Exception:
        print(f'Unable to create sec {n} for {c}')
        i = i - 1
    else:
        print('{} Created sec {} for {:15} in {} ({})'.format(i, str(n), str(c), str(sem), stat))
