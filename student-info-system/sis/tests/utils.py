from sis.models import (Student, Professor, Course, Major, Profile)
from django.contrib.auth.models import User
from decimal import Decimal


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
