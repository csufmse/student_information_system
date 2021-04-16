from decimal import Decimal
from datetime import datetime, timedelta

from django.contrib.auth.models import User

from sis.models import (Student, Professor, Course, Major, Profile, Semester)


def createAdmin(username=None, first=None, last=None, password=None):
    if first is None:
        first = username[0]
    if last is None:
        last = username[1:]
    if password is None:
        password = username + '1'
    user = User.objects.create(username=username, first_name=first, last_name=last)
    user.set_password(password)
    user.save()
    profile = user.profile
    profile.role = Profile.ACCESS_ADMIN
    profile.save()
    return user


def createProfessor(major=None, username=None, first=None, last=None, password=None):
    if first is None:
        first = username[0]
    if last is None:
        last = username[1:]
    if password is None:
        password = username + '1'
    user = User.objects.create(username=username, first_name=first, last_name=last)
    user.set_password(password)
    user.save()
    profile = user.profile
    profile.role = Profile.ACCESS_PROFESSOR
    profile.save()
    prof = Professor.objects.create(profile=profile, major=major)
    return prof


def createStudent(major=None, username=None, first=None, last=None, password=None):
    if first is None:
        first = username[0]
    if last is None:
        last = username[1:]
    if password is None:
        password = username + '1'
    user = User.objects.create(username=username, first_name=first, last_name=last)
    user.set_password(password)
    user.save()
    profile = user.profile
    profile.role = Profile.ACCESS_STUDENT
    profile.save()
    stud = Student.objects.create(profile=profile, major=major)
    return stud


def createCourse(major, num):
    return Course.objects.create(major=major,
                                 catalog_number=str(num),
                                 title='c' + str(num),
                                 description='course ' + str(num),
                                 credits_earned=Decimal('1.0'))


# dates are not dates, but number of days (plus or minus) from now.
# this lets you create all semester combinations.
def createSemester(year=2020,
                   date_registration_opens=0,
                   date_registration_closes=0,
                   date_started=0,
                   date_last_drop=0,
                   date_ended=0,
                   date_finalized=0,
                   session=Semester.FALL,
                   offsets=None):
    if offsets is not None:
        (date_registration_opens, date_registration_closes, date_started, date_last_drop,
         date_ended, date_finalized) = offsets

    dro = datetime.now() + timedelta(days=date_registration_opens)
    drc = datetime.now() + timedelta(days=date_registration_closes)
    ds = datetime.now() + timedelta(days=date_started)
    dld = datetime.now() + timedelta(days=date_last_drop)
    de = datetime.now() + timedelta(days=date_ended)
    df = datetime.now() + timedelta(days=date_finalized)
    semester = Semester.objects.create(date_registration_opens=dro,
                                       date_registration_closes=drc,
                                       date_started=ds,
                                       date_last_drop=dld,
                                       date_ended=de,
                                       date_finalized=df,
                                       session=session,
                                       year=year)
    return semester
