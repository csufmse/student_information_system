import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from random import randint

from sis.models import Course, Major

# from 3-9 pre-reqs for each major...


def randobj(objs):
    return objs.objects.all()[randint(0, objs.objects.count() - 1)]


error_count = 0

for m in Major.objects.all():
    to_add = randint(3, 9)
    added = {}
    for i in range(to_add):
        while True:
            c = randobj(Course)
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
