import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from sis.models import Section
from django.db import connection


def createData():

    ix = 1
    for sec in Section.objects.all():
        sec.refresh_reference_items()
        sec.save()
        ix = ix + 1
        if ix % 50 == 0:
            print(f'processed {ix}...')

    print(f'Processed {ix} sections in total.')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_sectionreferenceitem')


if __name__ == "__main__":
    createData()
