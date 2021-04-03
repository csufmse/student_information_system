import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from datetime import timedelta
from random import randint, random, shuffle
from django.db import connection

from sis.models import SemesterStudent, Student, TranscriptRequest, Semester


def createData():
    percent_that_have_request = 0.3
    percent_that_have_multiple = 0.25
    max_num_req = 3
    prob_fulfilled = 0.5

    error_count = 0
    studs = list(Student.objects.all())
    shuffle(studs)
    for s in studs[0:int(len(studs) * percent_that_have_request)]:

        if not len(s.semesters.all()):
            print(f'INFO: student {s.user.username} has no semesters, so no TR is ' +
                  'being created')
            continue
        earliest = s.semesters.order_by('date_started')[0].date_started
        latest = s.semesters.order_by('-date_ended')[0].date_ended
        period = (latest - earliest).days

        to_add = int(max_num_req * random())
        if random() > percent_that_have_multiple:
            to_add = 1

        dates_added = {}
        for j in range(to_add):
            while True:
                date_of = earliest + timedelta(days=randint(1, period))
                if date_of not in dates_added:
                    break
            dates_added[date_of] = True

            if random() < prob_fulfilled:
                date_fulfilled = date_of + timedelta(days=randint(1, 7))
            else:
                date_fulfilled = None

            tr = TranscriptRequest(student=s,
                                   date_requested=date_of,
                                   date_fulfilled=date_fulfilled)
            try:
                tr.save()
            except Exception:
                print(f'ERROR: could not add tr {tr} [stud={s.user_id}, req={date_of}, ' +
                      f'date_fulf={date_fulfilled}]')
                error_count = error_count + 1
            else:
                print(f'added request {tr}')

    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_transcriptrequest')


if __name__ == "__main__":
    createData()
