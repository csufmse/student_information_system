import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from random import randint, choices
from django.db import connection

from sis.models import Course, Major

# from 3-9 pre-reqs for each major...


def createData():
    error_count = 0

    courses = Course.objects.all()
    for m in Major.objects.all():
        to_add = randint(3, 9)
        added = {}

        # bias towards courses in their major
        weights = list(map((lambda course: 5 if course.major == m else 1), courses))

        for i in range(to_add):
            while True:
                c = choices(courses, weights=weights, k=1)[0]
                if c.id not in added:
                    break
            added[c.id] = True

            m.courses_required.add(c)
            try:
                m.save()
            except Exception:
                error_count = error_count + 1
                print(f'ERROR: could not add {c} to {m}')
            else:
                print(f'added {c} to {m}')

    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_major_courses_required')


if __name__ == "__main__":
    createData()
