import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from random import randint, choice
from django.db import connection

from sis.models import Course, CoursePrerequisite

percent_that_have_prereq = 0.6
max_num_prereqs = 3


def createData():
    # number of courses to add prereqs to:
    to_generate = int(Course.objects.count() * percent_that_have_prereq)

    courses = Course.objects.all()
    error_count = 0
    ii = 0
    while ii < to_generate:
        ii = ii + 1

        the_course = choice(courses)

        # number of prereqs to add to THIS course
        to_add = randint(0, max_num_prereqs)
        j = 0
        max_tries = 0
        while j < to_add and max_tries < 100:
            j = j + 1
            max_tries = max_tries + 1

            added = {the_course.id: True}
            while True:
                the_pre = choice(courses)
                if the_pre.id not in added:
                    break
            added[the_pre.id] = True

            if the_course.are_candidate_prerequisites_valid(candidate_list=[the_pre]):
                cp = CoursePrerequisite(course=the_course, prerequisite=the_pre)
                try:
                    cp.save()
                except Exception:
                    error_count = error_count + 1
                    print(f'ERROR: could not add prereq {the_pre} to {the_course}')
                    j = j - 1
                else:
                    print(f'added prereq {the_pre} to {the_course}')
            else:
                j = j - 1
    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_courseprerequisite')


if __name__ == "__main__":
    createData()
