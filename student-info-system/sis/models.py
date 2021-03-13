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


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    """ Student major """
    major = models.ForeignKey('Major',
                              on_delete=models.DO_NOTHING,
                              blank=True,
                              null=True)
    sections = models.ManyToManyField('Section',
                                      through='SectionStudent',
                                      related_name='students')

    # will be adding aggregate things here to replace dummy methods
    def class_level(self):
        return 'Freshman'

    def gpa(self):
        return 0.0

    def name(self):
        return self.user.first_name + ' ' + self.user.last_name

    def __str__(self):
        return self.name()


class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    """ Professor's department """
    major = models.ForeignKey('Major',
                              on_delete=models.DO_NOTHING,
                              blank=True,
                              null=True)

    def name(self):
        return self.user.first_name + ' ' + self.user.last_name

    def __str__(self):
        return self.name()


class Major(models.Model):
    abbreviation = UpperField('Abbreviation', max_length=6, primary_key=True)
    name = models.CharField('Name', max_length=256)
    description = models.CharField('Description', max_length=256, blank=True)
    professors = models.ManyToManyField(Professor,
                                        blank=True,
                                        related_name="prof")
    courses_required = models.ManyToManyField('Course',
                                              blank=True,
                                              related_name="required_by")

    def __str__(self):
        return self.abbreviation


class TranscriptRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_requested = models.DateField('Date Requested')
    date_fulfilled = models.DateField('Date Fulfilled', null=True, blank=True)

    def __str__(self):
        return self.student.name() + '@' + str(self.date_requested)


class Course(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE)
    catalogNumber = models.CharField('Number', max_length=20)
    title = models.CharField('Title', max_length=256)
    description = models.CharField('Description', max_length=256, blank=True)
    credits_earned = models.DecimalField('Credits',
                                         max_digits=2,
                                         decimal_places=1)
    prereqs = models.ManyToManyField('self', through='CoursePrerequisite')

    def major_name(self):
        return self.major.name

    major_name.short_description = 'Major Name'

    def name(self):
        return self.major.abbreviation + '-' + self.catalogNumber

    name.short_description = 'Course Name'

    def __str__(self):
        return self.name()


class CoursePrerequisite(models.Model):
    course = models.ForeignKey(Course,
                               related_name='a_course',
                               on_delete=models.CASCADE)
    prerequisite = models.ForeignKey(Course,
                                     related_name='a_prerequisite',
                                     on_delete=models.CASCADE)

    def __str__(self):
        return self.course.name() + ' requires ' + self.prerequisite.name()


class Semester(models.Model):
    name = models.CharField('Name', max_length=20)
    date_registration_opens = models.DateField('Registration Opens')
    date_started = models.DateField('Classes Start')
    date_last_drop = models.DateField('Last Drop')
    date_ended = models.DateField('Classes End')

    def __str__(self):
        return self.name


class SectionStudent(models.Model):
    section = models.ForeignKey('Section', on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(Student,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True)

    GRADE_A = 4
    GRADE_B = 3
    GRADE_C = 2
    GRADE_D = 1
    GRADE_F = 0
    GRADE = (
        (GRADE_A, 'A'),
        (GRADE_B, 'B'),
        (GRADE_C, 'C'),
        (GRADE_D, 'D'),
        (GRADE_F, 'F'),
    )
    grade = models.SmallIntegerField(
        choices=GRADE,
        default=GRADE_F,
        blank=True,
        null=True,
    )

    REGISTERED = 'Registered'
    AWAITING_GRADE = 'Done'
    GRADED = 'Graded'
    DROP_REQUESTED = 'DropReq'
    DROPPED = 'Dropped'
    STATUS = (
        (REGISTERED, 'Registered'),
        (AWAITING_GRADE, 'Awaiting Grade'),
        (GRADED, 'Graded'),
        (DROP_REQUESTED, 'Drop Requested'),
        (DROPPED, 'Dropped'),
    )
    status = models.CharField(
        'Course Status',
        choices=STATUS,
        default=REGISTERED,
        max_length=20,
    )

    def professor(self):
        return self.section.professor

    def name(self):
        return self.student.name() + '@' + self.section.name()

    def __str__(self):
        return self.name()


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.DO_NOTHING)
    semester = models.ForeignKey(Semester, on_delete=models.DO_NOTHING)
    number = models.IntegerField('Section Number',
                                 default=1,
                                 validators=[MinValueValidator(1)])
    capacity = models.IntegerField('Capacity',
                                   default=0,
                                   validators=[MinValueValidator(1)])
    hours = models.CharField('Hours', max_length=256)

    def course_name(self):
        return self.course.name

    course_name.short_description = 'Course Name'

    def professor_name(self):
        return self.professor.person.name

    professor_name.short_description = 'Professor Name'

    def semester_name(self):
        return self.semester.name

    semester_name.short_description = 'Semester'

    #  this will implemented as a custom manager -- BJM
    def registered(self):
        return self.sectionstudent_set.exclude(
            status=SectionStudent.DROPPED).count()

    def name(self):
        return self.course.name() + '-' + str(self.number)

    def __str__(self):
        return self.name()
