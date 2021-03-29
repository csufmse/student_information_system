import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from random import randint

from sis.models import Course, CoursePrerequisite

percent_that_have_prereq = 0.6
max_num_prereqs = 3


def randobj(objs):
    return objs.objects.all()[randint(0, objs.objects.count() - 1)]


# number of courses to add prereqs to:
to_generate = int(Course.objects.count() * percent_that_have_prereq)

ii = 0
while ii < to_generate:
    ii = ii + 1

    the_course = randobj(Course)

    # number of prereqs to add to THIS course
    to_add = randint(0, max_num_prereqs)
    j = 0
    max_tries = 0
    while j < to_add and max_tries < 100:
        j = j + 1
        max_tries = max_tries + 1

        the_pre = randobj(Course)
        while the_course == the_pre:
            the_pre = randobj(Course)

        if the_course.are_candidate_prerequisites_valid(candidate_list=[the_pre]):
            cp = CoursePrerequisite(course=the_course, prerequisite=the_pre)
            try:
                cp.save()
            except Exception:
                print(f'could not add prereq {the_pre} to {the_course}')
                j = j - 1
            else:
                print(f'added prereq {the_pre} to {the_course}')
        else:
            j = j - 1
