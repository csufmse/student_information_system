from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Case, ExpressionWrapper, F, Q, Sum, Max, Subquery, Value, When
from django.db.models.fields import (CharField, DateField, DecimalField, FloatField, IntegerField)
from django.db.models import Exists, OuterRef
from django.db.models.functions import Concat, Cast
from django.db.models.signals import post_save
from django.dispatch import receiver
from phone_field import PhoneField
from datetime import timedelta, datetime


class UpperField(models.CharField):
    """
    a subclass that returns the upper-cased version of its text. Effect is user cannot
    enter lower-case text
    """

    def __init__(self, *args, **kwargs):
        super(UpperField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).upper()


class Profile(models.Model):
    ACCESS_ADMIN = 'A'
    ACCESS_PROFESSOR = 'P'
    ACCESS_STUDENT = 'S'
    ROLES = ((ACCESS_ADMIN, 'Admin'), (ACCESS_PROFESSOR, 'Professor'), (ACCESS_STUDENT,
                                                                        'Student'))

    @classmethod
    def rolename_for(cls, aRole):
        return [item for item in Profile.ROLES if item[0] == aRole][0][1]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=ROLES, default=ACCESS_STUDENT)
    bio = models.CharField(max_length=256, blank=True)

    def has_student(self):
        has = False
        try:
            has = (self.student is not None)
        except Student.DoesNotExist:
            pass
        return has

    def has_professor(self):
        has = False
        try:
            has = (self.professor is not None)
        except Professor.DoesNotExist:
            pass
        return has

    @property
    def rolename(self):
        return Profile.rolename_for(self.role)

    @property
    def username(self):
        return self.user.username

    @property
    def name(self):
        return self.user.first_name + ' ' + self.user.last_name

    @property
    def name_sort(self):
        return self.user.last_name + ', ' + self.user.first_name

    def __str__(self):
        return f'{self.role} {self.user.username}'

    class Meta:
        ordering = ['user__username']


User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])


class ClassLevel:
    FRESHMAN = 'Freshman'
    SENIOR = 'Senior'
    JUNIOR = 'Junior'
    SOPHOMORE = 'Sophomore'
    LEVELS = (
        (FRESHMAN, FRESHMAN),
        (SOPHOMORE, SOPHOMORE),
        (JUNIOR, JUNIOR),
        (SENIOR, SENIOR),
    )
    CREDITS_FOR_LEVEL = {
        FRESHMAN: 0,
        SOPHOMORE: 30,
        JUNIOR: 60,
        SENIOR: 90,
    }

    @classmethod
    def level(cls, creds):
        lvl = ClassLevel.FRESHMAN
        if creds is None:
            pass
        elif creds > ClassLevel.CREDITS_FOR_LEVEL[ClassLevel.SENIOR]:
            lvl = ClassLevel.SENIOR
        elif creds > ClassLevel.CREDITS_FOR_LEVEL[ClassLevel.JUNIOR]:
            lvl = ClassLevel.JUNIOR
        elif creds > ClassLevel.CREDITS_FOR_LEVEL[ClassLevel.SOPHOMORE]:
            lvl = ClassLevel.SOPHOMORE

        return lvl


class Student(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    major = models.ForeignKey('Major', on_delete=models.CASCADE, blank=True, null=True)
    semesters = models.ManyToManyField('Semester',
                                       through='SemesterStudent',
                                       symmetrical=False,
                                       related_name='semester_students')

    class Meta:
        ordering = ['profile__user__username']

    @property
    def name(self):
        return f'{self.profile.user.first_name} {self.profile.user.last_name}'

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['profile__user__username']

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

    def remaining_required_courses(self, major=None):
        if major is None:
            major = self.major
        hist = self.course_history(passed=True)
        major_required = major.courses_required.all()
        major_required = major_required.exclude(
            id__in=Subquery(hist.values('section__course__id')))

        return major_required

    def requirements_met_list(self, major=None):
        if major is None:
            major = self.major
        return major.requirements_met_list(self)

    def prerequisites_met_list(self, course):
        return course.prerequisites_met_list(self)

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
        level = ClassLevel.level(creds)
        return level


class Professor(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    # Professor's department
    major = models.ForeignKey('Major', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['profile__user__username']

    @property
    def name(self):
        return self.profile.name

    def semesters_teaching(self):
        return Semester.objects.filter(
            section__semester__in=Subquery(self.section_set.values('semester__id'))).distinct()

    def __str__(self):
        return self.name


class Major(models.Model):
    abbreviation = UpperField('Abbreviation', max_length=6)
    title = models.CharField('Title', max_length=256)
    description = models.CharField('Description', max_length=256, blank=True)
    professors = models.ManyToManyField(Professor,
                                        symmetrical=False,
                                        blank=True,
                                        related_name="prof")
    courses_required = models.ManyToManyField('Course',
                                              blank=True,
                                              symmetrical=False,
                                              related_name="required_by")

    def requirements_met_list(self, student):
        return self.courses_required.annotate(met=Exists(
            student.sectionstudent_set.filter(section__course=OuterRef('pk'), grade__gt=0.0)))

    class Meta:
        ordering = ['abbreviation']

    @property
    def name(self):
        return self.title

    name.fget.short_description = 'Major Title'

    def __str__(self):
        return self.abbreviation


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

    major_name.fget.short_description = 'Major Title'

    @property
    def name(self):
        return self.major.abbreviation + '-' + str(self.catalog_number)

    name.fget.short_description = 'Course Name'

    @property
    def descr(self):
        return self.name + ': ' + self.title

    descr.fget.short_description = 'Course'

    def __str__(self):
        return self.name

    # don't want user specifying a prereq loop
    # with no list, validates existing prereqs.
    # with a list, tests if that list would cause a loop or not
    # (without storing it to db -- used for form validation)
    def are_candidate_prerequisites_valid(self, candidate_list=None):
        all_requirements_for_course = {}
        courses_to_visit = [self]
        loop_seen = False

        while len(courses_to_visit) > 0 and not loop_seen:
            course_to_check = courses_to_visit.pop()

            the_course_prereqs = []
            if course_to_check.prereqs.count():
                the_course_prereqs.extend(course_to_check.prereqs.all())
            if course_to_check.id == self.id and candidate_list is not None:
                the_course_prereqs.extend(candidate_list)

            if course_to_check not in all_requirements_for_course:
                all_requirements_for_course[course_to_check] = []

            for a_prereq in the_course_prereqs:
                courses_to_visit.append(a_prereq)

                all_requirements_for_course[course_to_check].append(a_prereq)
                # through a_prereq, course_to_check is dependent on everything a_prereq is.
                if a_prereq in all_requirements_for_course:
                    all_requirements_for_course[course_to_check].extend(
                        all_requirements_for_course[a_prereq])

            # did we just add a loop back to ourselves?
            if course_to_check in all_requirements_for_course[course_to_check]:
                loop_seen = True

        return not loop_seen

    def max_section_for_semester(self, semester):
        max_dict = self.section_set.filter(semester=semester).aggregate(Max('number'))
        max_num = max_dict['number__max']
        return max_num

    def prerequisites_met(self, student):
        remaining = self.prereqs.exclude(Exists(student.sectionstudent_set.filter(
            section__course=OuterRef('pk'), grade__gt=0.0)))
        return remaining.count() == 0

    def prerequisites_met_list(self, student):
        return self.prereqs.annotate(met=Exists(
            student.sectionstudent_set.filter(section__course=OuterRef('pk'), grade__gt=0.0)))


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


class SemesterManager(models.Manager):

    def get_queryset(self):
        """Overrides the models.Manager method"""
        qs = super(SemesterManager, self).get_queryset().annotate(
            session_order=Case(When(Q(session='FA'), then=0),
                               When(Q(session='WI'), then=1),
                               When(Q(session='SP'), then=2),
                               When(Q(session='SU'), then=3),
                               default=None,
                               output_field=IntegerField()),
            semester_order=Concat(Cast('year', CharField()),
                                  Value('-'),
                                  Cast('session_order', CharField()),
                                  output_field=CharField()),
        )
        return qs


class Semester(models.Model):
    objects = SemesterManager()

    FALL = 'FA'
    WINTER = 'WI'
    SPRING = 'SP'
    SUMMER = 'SU'
    SESSIONS = ((FALL, 'Fall'), (WINTER, 'Winter'), (SPRING, 'Spring'), (SUMMER, 'Summer'))
    SESSIONS_ORDER = [FALL, WINTER, SPRING, SUMMER]

    # convert Season code to name
    @classmethod
    def name_for_session(cls, abbrev):
        sname = [seas[1] for seas in Semester.SESSIONS if seas[0] == abbrev]
        if sname is not None and len(sname):
            return sname[0]

    date_registration_opens = models.DateField('Registration Opens')
    date_registration_closes = models.DateField('Registration Closes')
    date_started = models.DateField('Classes Start')
    date_last_drop = models.DateField('Last Drop')
    date_ended = models.DateField('Classes End')

    session = models.CharField('semester', choices=SESSIONS, default=FALL, max_length=6)
    year = models.IntegerField('year',
                               default=2000,
                               validators=[MinValueValidator(1900),
                                           MaxValueValidator(2300)])

    @property
    def session_name(self):
        return Semester.name_for_session(self.session)

    def professors_teaching(self):
        return User.annotated().filter(profile__professor__section__semester=self.id).distinct()

    def students_attending(self):
        return User.annotated().filter(
            profile__student__semesterstudent__semester=self.id).distinct()

    def registration_open(self, date=None):
        if date is None:
            date = datetime.now()
        return self.date_registration_opens <= date <= self.date_registration_closes

    def in_session(self, date=None):
        if date is None:
            date = datetime.now()
        return self.date_started <= date <= self.date_ended

    def preparing_grades(self, date=None):
        if date is None:
            date = datetime.now()
        return self.date_ended <= date <= self.date_ended + timedelta(days=14)

    def finalized(self, date=None):
        if date is None:
            date = datetime.now()
        return self.date_ended + timedelta(days=14) <= date

    def drop_possible(self, date=None):
        if date is None:
            date = datetime.now()
        return self.date_registration_opens <= date <= self.date_last_drop

    @property
    def name(self):
        return str(self.session) + "-" + str(self.year)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('session', 'year'),)
        ordering = ['date_started']


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
    IN_PROGRESS = 'In Progress'
    AWAITING_GRADE = 'Done'
    GRADED = 'Graded'
    DROP_REQUESTED = 'Drop Requested'
    DROPPED = 'Dropped'
    STATUSES = (
        (REGISTERED, REGISTERED),
        (IN_PROGRESS, IN_PROGRESS),
        (AWAITING_GRADE, AWAITING_GRADE),
        (GRADED, GRADED),
        (DROP_REQUESTED, DROP_REQUESTED),
        (DROPPED, DROPPED),
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
        return dict(self.GRADES).get(self.grade)

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
    location = models.CharField('Location', max_length=256)
    hours = models.CharField('Hours', max_length=256)

    students = models.ManyToManyField(Student,
                                      through='SectionStudent',
                                      symmetrical=False,
                                      related_name='section_students')

    REG_CLOSED = 'Closed'
    REG_OPEN = 'Open'
    IN_PROGRESS = 'In Progress'
    GRADING = 'Grading'
    GRADED = 'Graded'
    CANCELLED = 'Cancelled'
    STATUSES = (
        (REG_CLOSED, REG_CLOSED),
        (REG_OPEN, REG_OPEN),
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

    name.fget.short_description = 'Section'

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

    # the prof may have updated them; we may have changed professors...whyever
    def refresh_reference_items(self):
        for item in self.sectionreferenceitem_set.all():
            item.delete()
        if self.professor is not None:
            ix = 1
            for item in self.professor.referenceitem_set.filter(course=self.course):
                SectionReferenceItem.objects.create(item=item, section=self, index=ix)
                ix = ix + 1


class ReferenceItem(models.Model):
    REQUIRED = 'req'
    OPTIONAL = 'opt'
    RECOMMENDED = 'rec'
    SYLLABUS = 'syl'
    ASSIGNMENT = 'ass'
    TYPES = ((REQUIRED, 'Required'), (OPTIONAL, 'Optional'), (RECOMMENDED, 'Recommended'),
             (SYLLABUS, 'Syllabus'), (ASSIGNMENT, 'Assignment'))

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    title = models.CharField('Title', max_length=256)
    description = models.CharField('Description', blank=True, null=True, max_length=256)
    link = models.CharField('Link', blank=True, null=True, max_length=256)
    edition = models.CharField('Edition', blank=True, null=True, max_length=256)
    type = models.CharField(
        'Type',
        choices=TYPES,
        default=REQUIRED,
        max_length=3,
    )

    class Meta:
        unique_together = (('course', 'professor', 'title'),)

    @property
    def name(self):
        return f'{self.course}:{self.professor}/{self.title}'

    def __str__(self):
        return self.name


class SectionReferenceItem(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)
    item = models.ForeignKey(ReferenceItem, on_delete=models.CASCADE)
    index = models.IntegerField(verbose_name="#", default=1)

    class Meta:
        unique_together = (('section', 'item'), ('section', 'index'))

    @property
    def name(self):
        return f'{self.section}:{self.item}'

    def __str__(self):
        return self.name


# making it so users know about roles, but without overhead of subclassing


def access_role(self):
    return self.profile.rolename


def name(self):
    return self.profile.name


def student_gpa(self):
    return self.profile.student.gpa()


User.add_to_class('student_gpa', student_gpa)
User.add_to_class('access_role', access_role)
User.add_to_class('name', name)

# end


# Extend User to return annotated User objects
def uannotated(cls):
    return User.objects.annotate(
        role=F('profile__role',),
        name=Concat(F("first_name"), Value(' '), F("last_name")),
        name_sort=Concat(F("last_name"), Value(', '), F("first_name")),
    )


User.annotated = classmethod(uannotated)


def sannotated(cls):
    return Section.objects.annotate(course_descr=Concat(F('course__major'), Value('-'),
                                                        F('catalog_number'), Value(': '),
                                                        F('course__title')),)


Section.annotated = classmethod(sannotated)
