from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from phone_field import PhoneField


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



class Major(models.Model):
    abbreviation = UpperField('Abbreviation', max_length=6, primary_key=True)
    name = models.CharField('Name', max_length=256)
    description = models.CharField('Description', max_length=256, blank=True)
    professors = models.ManyToManyField(User, blank=True, related_name="prof")
    administrators = models.ManyToManyField(User, blank=True, related_name="admins")

    def __str__(self):
        return self.abbreviation

# This is an extension class for the default User class
class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField('Address',
                               max_length=256,
                               help_text='Your Mailing Address',
                               blank=True)
    phone = PhoneField(help_text='Your Primary Contact Phone', blank=True)
    major = models.ForeignKey(Major, on_delete=models.DO_NOTHING)

    def name(self):
        return self.fname + ' ' + self.lname

    def sort_name(self):
        return self.lname + ', ' + self.fname

    def __str__(self):
        return self.sort_name()


class Course(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE)
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

    def major_name(self):
        return self.major.name

    major_name.short_description = 'Major Name'

    def slug(self):
        return self.major.abbreviation + '-' + self.catalogNumber

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
