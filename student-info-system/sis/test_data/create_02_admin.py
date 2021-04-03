import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)  # noqa
django.setup()  # noqa

from django.contrib.auth.models import User
from django.db import connection

from sis.models import Admin

to_generate = 100

specs = (
    ('apollo', 'Apollo', 'Titania', 'apollo@olympus.org'),
    ('ares', 'Ares', 'Titania', 'ares@olympus.org'),
    ('artemis', 'Artemis', 'Titania', 'artemis@olympus.org'),
    ('athena', 'Athena', 'Titania', 'athena@olympus.org'),
    ('dionysus', 'Dionysus', 'Titania', 'dionysus@olympus.org'),
    ('hades', 'Hades', 'Titania', 'hades@olympus.org'),
    ('hera', 'Hera', 'Titania', 'hera@olympus.org'),
    ('hermes', 'Hermes', 'Titania', 'hermes@olympus.org'),
    ('zeus', 'Zeus', 'Titania', 'zeus@olympus.org'),
)


def createData():
    set_pass = True

    error_count = 0
    line = 1
    for (u, f, l, e) in specs[:to_generate]:
        usr = User(username=u, first_name=f, last_name=l, email=e)
        if set_pass:
            usr.set_password(u + '1')

        try:
            usr.save()
        except Exception:
            print(f'ERROR: Unable to create Admin(User) {line} {u} ({f} {l})')
            error_count = error_count + 1
            continue

        try:
            Admin.objects.create(user=usr)
        except Exception:
            print(f'failed creating Admin for user {usr.username}')
            error_count = error_count + 1
            continue

        print(f'Created admin {usr.username} ({usr.get_full_name()})')


def cleanData():
    list = []
    for ad in Admin.objects.all():
        list.append(str(ad.user_id))
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sis_admin"),
        cursor.execute('DELETE FROM auth_user WHERE id IN (' + (','.join(list) + ')'))


if __name__ == "__main__":
    createData(),
