import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from django.contrib.auth.models import User

from sis.models import Admin

set_pass = True

u = User(username='aphrodite',
         first_name='Aphrodite',
         last_name='Titania',
         email='aphrodite@olympus.org')
if set_pass:
    u.set_password(u.username + '1')
u.save()
a = Admin(user=u)
a.save()
u = User(username='apollo', first_name='Apollo', last_name='Titania', email='apollo@olympus.org')
if set_pass:
    u.set_password(u.username + '1')
u.save()
a = Admin(user=u)
a.save()
u = User(username='ares', first_name='Ares', last_name='Titania', email='ares@olympus.org')
if set_pass:
    u.set_password(u.username + '1')
u.save()
a = Admin(user=u)
a.save()
u = User(username='artemis',
         first_name='Artemis',
         last_name='Titania',
         email='artemis@olympus.org')
if set_pass:
    u.set_password(u.username + '1')
u.save()
a = Admin(user=u)
a.save()
u = User(username='athena', first_name='Athena', last_name='Titania', email='athena@olympus.org')
if set_pass:
    u.set_password(u.username + '1')
u.save()
a = Admin(user=u)
a.save()
u = User(username='dionysus',
         first_name='Dionysus',
         last_name='Titania',
         email='dionysus@olympus.org')
if set_pass:
    u.set_password(u.username + '1')
u.save()
a = Admin(user=u)
a.save()
u = User(username='hades', first_name='Hades', last_name='Titania', email='hades@olympus.org')
if set_pass:
    u.set_password(u.username + '1')
u.save()
a = Admin(user=u)
a.save()
u = User(username='hera', first_name='Hera', last_name='Titania', email='hera@olympus.org')
if set_pass:
    u.set_password(u.username + '1')
u.save()
a = Admin(user=u)
a.save()
u = User(username='hermes', first_name='Hermes', last_name='Titania', email='hermes@olympus.org')
if set_pass:
    u.set_password(u.username + '1')
u.save()
a = Admin(user=u)
a.save()
u = User(username='zeus', first_name='Zeus', last_name='Titania', email='zeus@olympus.org')
if set_pass:
    u.set_password(u.username + '1')
u.save()
a = Admin(user=u)
a.save()
