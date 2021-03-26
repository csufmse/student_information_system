import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from random import randint

from sis.models import Course, CoursePrerequisite

percent_that_have_prereq = 0.3
max_num_prereqs = 3


def randobj(objs):
    return objs.objects.all()[randint(0, objs.objects.count() - 1)]


for ii in range(int(Course.objects.count() * percent_that_have_prereq)):

    the_course = randobj(Course)

    to_add = randint(0, max_num_prereqs)
    for j in range(to_add):
        the_pre = randobj(Course)
        if the_course == the_pre:
            the_pre = randobj(Course)
        cp = CoursePrerequisite(course=the_course, prerequisite=the_pre)
        try:
            cp.save()
        except Exception:
            print(f'could not add prereq {the_pre} to {the_course}')
        else:
            print(f'added prereq {the_pre} to {the_course}')
