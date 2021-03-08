from django.db import models
from django.utils.translation import gettext_lazy as _
from phone_field import PhoneField


class Semester(models.Model):
    name = models.CharField('Semester Name', max_length=20, default='xxx')
    date_registration_opens = models.DateField('Registration Opens')
    date_started = models.DateField('Classes Start')
    date_last_drop = models.DateField('Last Drop')
    date_ended = models.DateField('Classes End')

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField('Name', max_length=128, help_text='Your Full Name')
    address = models.CharField('Address',
                               max_length=256,
                               help_text='Your Mailing Address',
                               blank=True)
    email = models.EmailField(help_text='Your Primary Email Address',
                              unique=True)
    phone = PhoneField(help_text='Your Primary Contact Phone', blank=True)
    is_active = models.BooleanField('Is Active?', default=False)
    is_admin = models.BooleanField('Is Admin?')
    is_semester_admin = models.BooleanField('Is Semester Admin?')
    is_class_admin = models.BooleanField('Is Class Admin?')
    is_grade_editor = models.BooleanField('Can Edit Grades?')

    def __str__(self):
        return self.name

    def can_log_in(self):
        return self.is_active or self.is_admin
