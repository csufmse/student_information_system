from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from phone_field import PhoneField
from django.db.models.signals import post_save
from django.dispatch import receiver


class UpperField(models.CharField):
    """
    a subclass that returns the upper-cased version of its text. Effect is user cannot
    enter lower-case text
    """
    def __init__(self, *args, **kwargs):
        super(UpperField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).upper()

class Semester(models.Model):
    name = models.CharField('Name', max_length=20, default='xxx')
    date_registration_opens = models.DateField('Registration Opens')
    date_started = models.DateField('Classes Start')
    date_last_drop = models.DateField('Last Drop')
    date_ended = models.DateField('Classes End')

    def __str__(self):
        return self.name


# This is an extension class for the default User class
class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField('Address',
                               max_length=256,
                               help_text='Your Mailing Address',
                               blank=True)
    phone = PhoneField(help_text='Your Primary Contact Phone', blank=True)

    @property
    def name(self):
        return self.user.first_name + ' ' + self.user.last_name

    @property
    def sort_name(self):
        return self.user.last_name + ', ' + self.user.first_name

    def __str__(self):
        return self.sort_name

# https://simpleisbetterthancomplex.com/tutorial/2016/11/23/how-to-add-user-profile-to-django-admin.html
@receiver(post_save, sender=User)
def create_or_update_user_person(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user=instance)
    instance.person.save()


class Department(models.Model):
    abbreviation = UpperField('Abbreviation', max_length=6, primary_key=True)
    name = models.CharField('Name', max_length=256)
    description = models.CharField('Description', max_length=256, blank=True)
    professors = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.abbreviation


class Major(models.Model):
    abbreviation = UpperField('Abbreviation', max_length=6, primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=256)
    description = models.CharField('Description', max_length=256, blank=True)

    def department_name(self):
        return self.department.name

    department_name.short_description = 'Department Name'

    def __str__(self):
        return self.abbreviation


class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    catalogNumber = models.CharField('Number', max_length=20)
    title = models.CharField('Title', max_length=256)
    description = models.CharField('Description', max_length=256, blank=True)
    credits_earned = models.DecimalField('Credits',
                                         max_digits=2,
                                         decimal_places=1)

    GRADING_METHOD_CHOICES = [('GR', 'Graded'), ('CR', 'Credit/No Credit')]
    grading_type = models.CharField(max_length=2,
                                    choices=GRADING_METHOD_CHOICES,
                                    default='GR')

    def department_name(self):
        return self.department.name

    department_name.short_description = 'Department Name'

    def slug(self):
        return self.department.abbreviation + '-' + self.catalogNumber

    slug.short_description = 'Course Number'

    def __str__(self):
        return self.slug()


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    professor = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    semester = models.ForeignKey(Semester, on_delete=models.DO_NOTHING)
    number = models.IntegerField('Section Number',
                                 default=1,
                                 validators=[MinValueValidator(1)])
    textbooks = models.CharField('Textbooks', max_length=256, blank=True)
    capacity = models.IntegerField('Capacity',
                                   default=0,
                                   validators=[MinValueValidator(1)])
    waitlist_capacity = models.IntegerField('Waitlist Capacity',
                                            default=0,
                                            validators=[MinValueValidator(0)])

    def course_name(self):
        return self.course.name

    course_name.short_description = 'Course Name'

    def professor_name(self):
        return self.professor.person.name

    professor_name.short_description = 'Professor Name'

    def semester_name(self):
        return self.semester.name

    semester_name.short_description = 'Semester'

    def slug(self):
        return self.course.slug() + '-' + str(self.number)

    slug.short_description = 'Section'

    def registered(self):
        return 0

    def waitlisted(self):
        return 0

    def __str__(self):
        return self.slug()
