from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Case, Count, ExpressionWrapper, F, Q, Sum, Subquery
from django.db.models import Value
from django.db.models import Value as V
from django.db.models import When
from django.db.models.fields import (CharField, DateField, DecimalField, FloatField, IntegerField)
from django.db.models.functions import Concat
from django.db.models.signals import post_save
from django.dispatch import receiver
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


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        ordering = ['user__username']

    @property
    def username(self):
        return self.user.username

    @property
    def name(self):
        return self.user.first_name + ' ' + self.user.last_name

    def __str__(self):
        return self.name


class Student(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    major = models.ForeignKey('Major', on_delete=models.CASCADE, blank=True, null=True)
    semesters = models.ManyToManyField('Semester',
                                       through='SemesterStudent',
                                       symmetrical=False,
                                       related_name='semester_students')
    sections = models.ManyToManyField('Section',
                                      through='SectionStudent',
                                      symmetrical=False,
                                      related_name='section_students')

    class Meta:
        ordering = ['user__username']

    def course_history(self, graded=False, passed=False, required=False, prereqs_for=None):
        hist = self.sectionstudent_set.all()
        if passed:
            graded = True
        if graded:
            hist = hist.filter(status__exact='Graded')
        if passed:
            hist = hist.filter(grade__gt=0)
        if required:
            major_required = self.major.courses_required.all()
            hist = hist.filter(section__course__in=Subquery(major_required.all().values('id')))
        if prereqs_for is not None:
            course_prereqs = CoursePrerequisite.objects.filter(course=prereqs_for)
            hist = hist.filter(
                section__course__in=Subquery(course_prereqs.values('prerequisite')))

        return hist

    def remaining_required_courses(self):
        hist = self.course_history(passed=True)
        major_required = self.major.courses_required.all()
        major_required = major_required.exclude(
            id__in=Subquery(hist.values('section__course__id')))

        return major_required

    def credits_earned(self):
        completed = self.course_history(passed=True).aggregate(
            Sum('section__course__credits_earned'))['section__course__credits_earned__sum']

        if completed is None:
            completed = 0
        return completed

    def gpa(self):
        completed = self.course_history(graded=True)
        grade_points = 0
        credits_attempted = 0
        for ss in completed:
            credits_attempted = credits_attempted + ss.section.course.credits_earned
            grade_points = grade_points + ss.grade_points

        if credits_attempted == 0:
            return 0.0
        return grade_points / float(credits_attempted)

    def class_level(self):
        creds = self.credits_earned()
        level = 'Freshman'
        if creds is None:
            pass
        if creds > 90:
            level = 'Senior'
        elif creds > 60:
            level = 'Junior'
        elif creds > 30:
            level = 'Sophomore'
        return level

    @property
    def name(self):
        return self.user.first_name + ' ' + self.user.last_name

    def __str__(self):
        return self.name


class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Professor's department
    major = models.ForeignKey('Major', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['user__username']

    @property
    def name(self):
        return self.user.first_name + ' ' + self.user.last_name

    def __str__(self):
        return self.name


class Major(models.Model):
    abbreviation = UpperField('Abbreviation', max_length=6, primary_key=True)
    name = models.CharField('Name', max_length=256)
    description = models.CharField('Description', max_length=256, blank=True)
    professors = models.ManyToManyField(Professor,
                                        symmetrical=False,
                                        blank=True,
                                        related_name="prof")
    courses_required = models.ManyToManyField('Course',
                                              blank=True,
                                              symmetrical=False,
                                              related_name="required_by")
    class Meta:
        ordering = ['abbreviation']


    def __str__(self):
        return self.abbreviation


class TranscriptRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_requested = models.DateField('Date Requested')
    date_fulfilled = models.DateField('Date Fulfilled', null=True, blank=True)

    class Meta:
        unique_together = (('student', 'date_requested'),)
        ordering = ['student']

    def __str__(self):
        return self.student.name + '@' + str(self.date_requested)


class Course(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE)
    catalog_number = models.CharField('Number', max_length=20)
    title = models.CharField('Title', max_length=256)
    description = models.CharField('Description', max_length=256, blank=True)
    credits_earned = models.DecimalField('Credits', max_digits=2, decimal_places=1)
    prereqs = models.ManyToManyField('self', symmetrical=False, through='CoursePrerequisite')

    class Meta:
        unique_together = (('major', 'catalog_number'),)
        ordering = ['major', 'catalog_number', 'title']

    @property
    def major_name(self):
        return self.major.name

    major_name.fget.short_description = 'Major Name'

    @property
    def name(self):
        return self.major.abbreviation + '-' + str(self.catalog_number)

    name.fget.short_description = 'Course Name'

    @property
    def descr(self):
        return self.name + ':' + self.title

    descr.fget.short_description = 'Course'

    def __str__(self):
        return self.name


class CoursePrerequisite(models.Model):
    course = models.ForeignKey(Course, related_name='a_course', on_delete=models.CASCADE)
    prerequisite = models.ForeignKey(Course,
                                     related_name='a_prerequisite',
                                     on_delete=models.CASCADE)

    class Meta:
        unique_together = (('course', 'prerequisite'),)
        ordering = ['course', 'prerequisite']

    def __str__(self):
        return self.course.name + ' requires ' + self.prerequisite.name


class Semester(models.Model):
    date_registration_opens = models.DateField('Registration Opens')
    date_started = models.DateField('Classes Start')
    date_last_drop = models.DateField('Last Drop')
    date_ended = models.DateField('Classes End')
    FALL = 'FA'
    SPRING = 'SP'
    SUMMER = 'SU'
    WINTER = 'WI'
    SEASONS = ((FALL, 'Fall'), (SPRING, 'Spring'), (SUMMER, 'Summer'), (WINTER, 'Winter'))
    semester = models.CharField('semester', choices=SEASONS, default='FA', max_length=6)
    year = models.IntegerField('year',
                               default=2000,
                               validators=[MinValueValidator(1900),
                                           MaxValueValidator(2300)])

    # students = models.ManyToManyField(Student,
    #                                   through='SemesterStudent',
    #                                   symmetrical=False,
    #                                   related_name='semester_students')

    class Meta:
        unique_together = (('semester', 'year'),)
        ordering = ['date_registration_opens']

    @property
    def name(self):
        return str(self.semester) + "-" + str(self.year)

    def __str__(self):
        return self.name


class SemesterStudent(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('semester', 'student'),)
        ordering = ['semester', 'student']

    @property
    def name(self):
        return str(self.student) + "@" + str(self.semester)

    def __str__(self):
        return self.name


class SectionStudentManager(models.Manager):

    def get_queryset(self):
        """Overrides the models.Manager method"""
        qs = super(SectionStudentManager, self).get_queryset().annotate(
            credits_earned=Case(When(Q(status='Graded') & Q(grade__isnull=False) & Q(grade__gt=0),
                                     then=F('section__course__credits_earned')),
                                When(Q(status='Graded') & Q(grade__isnull=False), then=0),
                                default=None,
                                output_field=DecimalField()),
            grade_points=ExpressionWrapper(F('grade') * F('section__course__credits_earned'),
                                           output_field=FloatField()),
        )
        return qs


class SectionStudent(models.Model):
    # Extra fields here!
    objects = SectionStudentManager()

    section = models.ForeignKey('Section', on_delete=models.CASCADE, null=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True, blank=True)

    GRADE_A = 4
    GRADE_B = 3
    GRADE_C = 2
    GRADE_D = 1
    GRADE_F = 0
    GRADES = (
        (GRADE_A, 'A'),
        (GRADE_B, 'B'),
        (GRADE_C, 'C'),
        (GRADE_D, 'D'),
        (GRADE_F, 'F'),
    )
    grade = models.SmallIntegerField(
        choices=GRADES,
        default=None,
        blank=True,
        null=True,
    )

    REGISTERED = 'Registered'
    AWAITING_GRADE = 'Done'
    GRADED = 'Graded'
    DROP_REQUESTED = 'Drop Requested'
    DROPPED = 'Dropped'
    WAITLISTED = 'Waitlisted'
    STATUSES = (
        (REGISTERED, REGISTERED),
        (AWAITING_GRADE, AWAITING_GRADE),
        (GRADED, GRADED),
        (DROP_REQUESTED, DROP_REQUESTED),
        (DROPPED, DROPPED),
        (WAITLISTED, WAITLISTED),
    )
    status = models.CharField(
        'Student Status',
        choices=STATUSES,
        default=REGISTERED,
        max_length=20,
    )

    class Meta:
        unique_together = (('section', 'student'),)
        ordering = ['section', 'student']

    @property
    def professor(self):
        return self.section.professor

    @property
    def letter_grade(self):
        return dict(GRADES).get(self.grade)

    letter_grade.fget.short_description = 'Grade Assigned'

    @property
    def name(self):
        return self.student.name + '@' + self.section.name

    def __str__(self):
        return self.name


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    number = models.IntegerField('Section Number', default=1, validators=[MinValueValidator(1)])
    capacity = models.IntegerField('Capacity', default=0, validators=[MinValueValidator(1)])
    hours = models.CharField('Hours', max_length=256)

    students = models.ManyToManyField(Student,
                                      through='SectionStudent',
                                      symmetrical=False,
                                      related_name='section_students')

    CLOSED = 'Closed'
    OPEN = 'Open'
    IN_PROGRESS = 'In Progress'
    GRADING = 'Grading'
    GRADED = 'Graded'
    CANCELLED = 'Cancelled'
    STATUSES = (
        (CLOSED, CLOSED),
        (OPEN, OPEN),
        (IN_PROGRESS, IN_PROGRESS),
        (GRADING, GRADING),
        (GRADED, GRADED),
        (CANCELLED, CANCELLED),
    )
    status = models.CharField(
        'Section Status',
        choices=STATUSES,
        default=CLOSED,
        max_length=20,
    )

    class Meta:
        unique_together = (('course', 'semester', 'number'),)
        ordering = ['semester', 'course', 'number']

    @property
    def name(self):
        return self.course_name + '-' + str(self.number)

    @property
    def course_title(self):
        return self.course.title

    course_title.fget.short_description = 'Course Title'

    @property
    def course_name(self):
        return self.course.name

    course_name.fget.short_description = 'Course Name'

    @property
    def professor_name(self):
        return self.professor.name

    professor_name.fget.short_description = 'Professor Name'

    @property
    def semester_name(self):
        return self.semester.name

    semester_name.fget.short_description = 'Semester'

    @property
    def registered(self):
        return self.sectionstudent_set.exclude(status=SectionStudent.DROPPED).count()

    registered.fget.short_description = 'Count of Registered'

    @property
    def seats_remaining(self):
        return self.capacity - self.registered

    seats_remaining.fget.short_description = 'Seats Remaining'

    def __str__(self):
        return self.name


# making it so users know about roles, but without overhead of subclassing


def access_role(self):
    is_admin = Admin.objects.filter(user_id=self.id).count() > 0
    is_student = Student.objects.filter(user_id=self.id).count() > 0
    is_professor = Professor.objects.filter(user_id=self.id).count() > 0
    if is_admin:
        return 'Admin'
    elif is_professor:
        return 'Professor'
    elif is_student:
        return 'Student'
    else:
        return 'Unknown'


def name(self):
    return self.first_name + ' ' + self.last_name


User.add_to_class('access_role', access_role)
User.add_to_class('name', name)

# end


# Extend User to return annotated User objects
def uannotated(cls):
    return User.objects.annotate(
        access_role=Case(
            When(student__user__isnull=False, then=Value('Student')),
            When(admin__user__isnull=False, then=Value('Admin')),
            When(professor__user__isnull=False, then=Value('Professor')),
            default=Value('Unknown'),
            output_field=models.CharField(),
        ),
        name=Concat(F("first_name"), Value(' '), F("last_name")),
        name_sort=Concat(F("last_name"), Value(', '), F("first_name")),
    ).exclude(access_role='Unknown')


User.annotated = classmethod(uannotated)


def sannotated(cls):
    return Section.objects.annotate(course_descr=Concat(F('course__major'), Value('-'),
                                                        F('catalog_number'), Value(': '),
                                                        F('course__title')),)


Section.annotated = classmethod(sannotated)
