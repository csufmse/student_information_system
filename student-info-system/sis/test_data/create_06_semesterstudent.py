import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from random import randint, random, shuffle
from django.db import connection

from sis.models import Semester, SemesterStudent, Student


def createData():
    prob_of_no_semesters = 0.1
    prob_of_summer = 0.25

    error_count = 0

    semesters = Semester.objects.all().order_by("date_started")
    stud_list = list(Student.objects.all())
    shuffle(stud_list)
    stud_count = int(len(stud_list) * (1.0 - prob_of_no_semesters))
    for stud in stud_list[0:stud_count]:

        start = randint(0, semesters.count() - 1)
        stop = start + randint(1, 12)
        stop = min(stop, len(semesters) - 1)
        print(f'Student {stud.name} will attend from {semesters[start].session_name}-' +
              f'{semesters[start].year} ' +
              f'to {semesters[stop].session_name}-{semesters[stop].year}')
        for sem in semesters[start:stop]:
            if sem.semester == Semester.SUMMER and random() > prob_of_summer:
                continue

            sems = SemesterStudent(student=stud, semester=sem)
            try:
                sems.save()
            except Exception:
                print(f'ERROR: could not add {sem} to {stud}')

    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sis_semesterstudent")


if __name__ == "__main__":
    createData()
