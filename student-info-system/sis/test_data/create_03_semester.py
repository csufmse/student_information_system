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
            print(f'Creating {session} {next.year} ...')
            try:
                Semester.objects.create(year=next.year,
                                        date_registration_opens=next - timedelta(days=60),
                                        date_registration_closes=next - timedelta(days=7),
                                        date_started=next,
                                        date_last_drop=next + timedelta(days=14),
                                        date_ended=next + timedelta(weeks=11),
                                        session=session)
            except IntegrityError as e:
                if 'UNIQUE constraint' in e.args[0]:
                    print(
                        f'ERROR: {next.year}/{session} already exists. (did you drop all ' +
                        'data before doing this?)'
                    )
                else:
                    print(
                        f'ERROR: There was a problem saving {next.year}/{session} to ' +
                        'the database.'
                    )

            next = next + timedelta(days=90)

    # make sure we have at least one semester open for registration
    current_semester = Semester.objects.get(date_started__lte=datetime.now(),
                                            date_ended__gte=datetime.now())
    current_semester.date_registration_opens = datetime.now() - timedelta(days=1)
    current_semester.date_registration_closes = datetime.now() + timedelta(days=21)
    current_semester.date_last_drop = datetime.now() + timedelta(days=28)
    current_semester.date_ended = datetime.now() + timedelta(days=29)
    current_semester.save()


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_semester')


if __name__ == "__main__":
    createData()
