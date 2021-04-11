import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from datetime import date, timedelta, datetime
from django.db import connection

from sis.models import Semester


def createData():
    for year in range(2015, 2022):
        next = date(year, 9, 15)
        for session in Semester.SESSIONS_ORDER:
            print(f'Creating {year} {session}...')
            Semester.objects.create(year=year,
                                    date_registration_opens=next - timedelta(days=60),
                                    date_registration_closes=next - timedelta(days=7),
                                    date_started=next,
                                    date_last_drop=next + timedelta(days=14),
                                    date_ended=next + timedelta(weeks=11),
                                    session=session)
            next = next + timedelta(days=90)

    # make sure we have at least one semester open for registration
    last_sem = Semester.objects.order_by('-date_started')[0]
    last_sem.date_registration_opens = datetime.now() - timedelta(days=1)
    last_sem.save()


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_semester')


if __name__ == "__main__":
    createData()
