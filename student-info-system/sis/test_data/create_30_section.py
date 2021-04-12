import os
import sys
from random import randint, choice, shuffle, random
from datetime import datetime

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from sis.models import Course, Major, Professor, Section, Semester
from django.db import connection

to_generate = 1000

capacities = (10,) * 3 + (30,) * 11 + (100,) * 3

durations = (30,) * 7 + (60,) * 6 + (90,) * 3 + (180,) * 3

days = ('M', 'T', 'W', 'Th', 'F', 'Sa', 'Su')


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


def createData():
    # set low to generate multiple sections per semester, count() to spread
    # them across all courses
    # course_max = 10
    course_count = len(Course.objects.all())

    courses = list(Course.objects.all())
    shuffle(courses)
    courses = courses[0:course_count]

    # concentrate on how many of the latest sections?
    # sem_count = 1
    sem_count = len(Semester.objects.all())

    now = datetime.now()
    semesters = Semester.objects.order_by('-date_started')[0:sem_count]

    error_count = 0
    i = 0
    while i < to_generate:
        i = i + 1

        c = choice(courses)

        ps = Professor.objects.filter(major=c.major)
        if ps.count() == 0:
            print(f'ERROR: No teachers for {c} ...')
            error_count = error_count + 1
            i = i - 1
            continue

        p = choice(ps)
        d = choose_days()
        h = choose_hours()
        cap = choice(capacities)

        sem = choice(semesters)

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

        number_of_sections = Section.objects.filter(course=c, semester=sem).count()
        n = number_of_sections + 1

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
            i = i - 1
        else:
            print('{} Created sec {} for {:15} in {} ({})'.format(i, str(n), str(c), str(sem),
                                                                  stat))

    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_section')


if __name__ == "__main__":
    createData()
