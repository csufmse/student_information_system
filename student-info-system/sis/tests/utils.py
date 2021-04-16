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
def createSemester(year=None,
                   date_registration_opens=None,
                   date_registration_closes=None,
                   date_started=None,
                   date_last_drop=None,
                   date_ended=None,
                   date_finalized=None,
                   session=None):
    if year is None:
        year = 2020
    if session is None:
        session = Semester.FALL
    dro = datetime.now()
    if date_registration_opens is not None:
        dro += timedelta(days=date_registration_opens)
    drc = datetime.now()
    if date_registration_closes is not None:
        drc += timedelta(days=date_registration_closes)
    ds = datetime.now()
    if date_started is not None:
        ds += timedelta(days=date_started)
    dld = datetime.now()
    if date_last_drop is not None:
        dld += timedelta(days=date_last_drop)
    de = datetime.now()
    if date_ended is not None:
        de += timedelta(days=date_ended)
    df = datetime.now()
    if date_finalized is not None:
        df += timedelta(days=date_finalized)
    semester = Semester.objects.create(date_registration_opens=dro,
                                       date_registration_closes=drc,
                                       date_started=ds,
                                       date_last_drop=dld,
                                       date_ended=de,
                                       date_finalized=df,
                                       session=session,
                                       year=year)
    return semester
