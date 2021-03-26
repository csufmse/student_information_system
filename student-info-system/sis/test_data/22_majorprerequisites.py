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


for m in Major.objects.all():
    to_add = randint(3, 9)
    for i in range(to_add):
        c = randobj(Course)
        m.courses_required.add(c)
        try:
            m.save()
        except Exception:
            print(f'could not add {c} to {m}')
        else:
            print(f'added {c} to {m}')
