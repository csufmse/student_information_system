from sis.models import (Student, Professor, Admin, Course, Major)
from django.contrib.auth.models import User
from decimal import Decimal

def createAdmin(username=None):
    user = User.objects.create(username=username, first_name=username[0], last_name=username[1:])
    user.set_password(username+'1')
    user.save()
    ad = Admin.objects.create(user=user)
    return ad


def createProfessor(major=None, username=None):
    user = User.objects.create(username=username, first_name=username[0], last_name=username[1:])
    user.set_password(username+'1')
    user.save()
    prof = Professor.objects.create(user=user, major=major)
    return prof

def createStudent(major=None, username=None):
    user = User.objects.create(username=username, first_name=username[0], last_name=username[1:])
    user.set_password(username+'1')
    user.save()
    stud = Student.objects.create(user=user, major=major)
    return stud


def createCourse(major, num):
    return Course.objects.create(major=major,
                                 catalog_number=str(num),
                                 title='c' + str(num),
                                 description='course '+str(num),
                                 credits_earned=Decimal('1.0'))

