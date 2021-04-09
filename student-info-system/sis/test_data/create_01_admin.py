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
from sis.models import Profile
from random import choices

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


def set_choice_attr(instance, attribute_name, options, weights):
    if len(options) != len(weights):
        print(f'{attribute_name}: {len(options)} {len(weights)}')
        raise Exception()
    aChoice = choices(options, weights=weights)[0][0]
    setattr(instance, attribute_name, aChoice)


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
            profile = usr.profile
            profile.role = Profile.ACCESS_ADMIN

            set_choice_attr(profile, 'demo_age', Profile.AGE, (3, 10, 5, 1, 1, 1, 1, 1, 3))
            set_choice_attr(profile, 'demo_race', Profile.RACE, (10, 1, 5, 3, 1, 5))
            set_choice_attr(profile, 'demo_gender', Profile.GENDER, (7, 8, 1, 1, 3))
            set_choice_attr(profile, 'demo_employment', Profile.WORK_STATUS, (5, 3, 2, 1, 2, 3))
            set_choice_attr(profile, 'demo_income', Profile.ANNUAL_HOUSEHOLD_INCOME,
                            (1, 2, 5, 3, 4))
            set_choice_attr(profile, 'demo_education', Profile.HIGHEST_FAMILY_EDUCATION,
                            (3, 3, 3, 2, 5, 3, 2, 3))
            set_choice_attr(profile, 'demo_orientation', Profile.ORIENTATION, (95, 6, 2, 1, 10))
            set_choice_attr(profile, 'demo_marital', Profile.MARITAL_STATUS, (10, 4, 3, 1, 4))
            set_choice_attr(profile, 'demo_disability', Profile.DISABILITY, (10, 4, 2, 2, 3, 6))
            set_choice_attr(profile, 'demo_veteran', Profile.VETERAN_STATUS, (8, 2, 4))
            set_choice_attr(profile, 'demo_citizenship', Profile.CITIZENSHIP, (10, 6, 4, 4, 6))

            profile.save()
        except Exception:
            print(f'ERROR: Unable to create Admin(User) {line} {u} ({f} {l})')
            error_count = error_count + 1
            continue

        print(f'Created admin {usr.username} ({usr.get_full_name()})')


def cleanData():
    list = []
    for ad in Profile.objects.filter(role=Profile.ACCESS_ADMIN):
        list.append(str(ad.user.id))
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sis_profile WHERE user_id in (" + (','.join(list)) + ')')
        cursor.execute('DELETE FROM auth_user WHERE id IN (' + (','.join(list) + ')'))


if __name__ == "__main__":
    createData(),
