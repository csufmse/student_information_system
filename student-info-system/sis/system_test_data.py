from datetime import date
from django.contrib.auth.models import User
from .models import (Student, Professor, Major, TranscriptRequest, Course,
                     CoursePrerequisite, Semester, SectionStudent, Section)

# Creation of test data (for developing, demoing, maybe acceptance testing)
#
# Access one or all models at once. Ideal for setting up FKs and messing around.
#
# How to create more data for an existing model:
#   1. add something to create(). For courtesy, add something to fetch
#       BEST TO USE field names. Don't be lazy like...
#
# How to add a new model:
#   1. do the obvious..
#   2. In fetch(), if model requires others, add a OtherModel.fetch()
#      (too dangerous to add this into create() -- take care of it yourself!
#   2. Add the model to createAll() and fetchAll()
#      (in the order of dependence)
#
# How to use this to refresh database:
#   1. delete db.sqlite3
#   2. manage.py makemigrations
#   3. manage.py migrate
#   4. manage.py createsuperuser
#      (this is the "admin" userid. Use our standard password for it)
#   5. manage.py shell
#   6. from sis.system_test_data import *
#   7. createAll()
#
# How to use this to play around in the shell:
#   (basically a fast way to access created objects)
#   1. manage.py shell
#   2. from sis.system_test_data import *
#   3. fetchAll()
#   3.5. If you only need one Models's worth do it directly: Majors.fetchAll()
#   4. Access objects with things like "Majors.arch" (NOTE THE "s")


class Semesters():

    @classmethod
    def create(cls) -> None:
        Semesters.s1 = Semester(date_registration_opens=date(2020, 11, 25),
                                date_started=date(2021, 1, 21),
                                date_last_drop=date(2021, 2, 4),
                                date_ended=date(2021, 5, 21),
                                semester='SP',
                                year=2021)
        Semesters.s1.save()
        Semesters.s2 = Semester(date_registration_opens=date(2021, 3, 23),
                                date_started=date(2021, 6, 15),
                                date_last_drop=date(2021, 7, 5),
                                date_ended=date(2021, 8, 6),
                                semester='SU',
                                year=2021)
        Semesters.s2.save()

    @classmethod
    def fetch(cls) -> None:
        Semesters.s0 = Semester.objects.filter(semester='FA', year=2000).get()
        Semesters.s1 = Semester.objects.filter(semester='SP', year=2021).get()
        Semesters.s2 = Semester.objects.filter(semester='SU', year=2021).get()


class Majors():

    @classmethod
    def create(cls) -> None:
        Major.cpsc = Major(abbreviation='CPSC',
                           name="Computer Science",
                           description="bits and byte, oh my!")
        Major.cpsc.save()
        Major.engl = Major(
            abbreviation='ENGL',
            name='English',
            description='Composition, Literature, and Rhetoric. Not Grunting.')
        Major.engl.save()
        Major.arch = Major(abbreviation='ARCH',
                           name='Architecture',
                           description='Buildings and Ditches')
        Major.arch.save()
        Major.phys = Major(abbreviation='PHYS',
                           name='Physics',
                           description='Why Things Break')
        Major.phys.save()

    @classmethod
    def fetch(cls) -> None:
        Major.cpsc = Major.objects.filter(abbreviation='CPSC').get()
        Major.phys = Major.objects.filter(abbreviation='PHYS').get()
        Major.arch = Major.objects.filter(abbreviation='ARCH').get()
        Major.engl = Major.objects.filter(abbreviation='ENGL').get()


class Courses():

    @classmethod
    def create(cls) -> None:
        Courses.cpsc101 = Course(major=Majors.cpsc,
                                 catalogNumber='101',
                                 title='Intro to Programming',
                                 credits_earned=3.0)
        Courses.cpsc101.save()
        Courses.cpsc345 = Course(major=Majors.cpsc,
                                 catalogNumber='345',
                                 title='Data Structures',
                                 credits_earned=3.0)
        Courses.cpsc345.save()
        Courses.engl218 = Course(major=Majors.engl,
                                 catalogNumber='218',
                                 title='Technical Writing',
                                 credits_earned=3.0)
        Courses.engl218.save()
        Courses.engl255 = Course(major=Majors.engl,
                                 catalogNumber='255',
                                 title='Bible as Literature',
                                 credits_earned=3.0)
        Courses.engl255.save()
        Courses.phys405 = Course(major=Majors.phys,
                                 catalogNumber='405',
                                 title='Quantum Mechanics',
                                 credits_earned=4.0)
        Courses.phys405.save()
        Courses.phys406 = Course(major=Majors.phys,
                                 catalogNumber='406',
                                 title='Advanced Quantum Mechanics',
                                 credits_earned=4.0)
        Courses.phys406.save()

    @classmethod
    def fetch(cls) -> None:
        Majors.fetch()
        Courses.cpsc101 = Course.objects.filter(major=Majors.cpsc,
                                                catalogNumber='101').get()
        Courses.cpsc345 = Course.objects.filter(major=Majors.cpsc,
                                                catalogNumber='345').get()
        Courses.engl218 = Course.objects.filter(major=Majors.engl,
                                                catalogNumber='218').get()
        Courses.engl255 = Course.objects.filter(major=Majors.engl,
                                                catalogNumber='405').get()
        Courses.phys405 = Course.objects.filter(major=Majors.phys,
                                                catalogNumber='405').get()
        Courses.phys406 = Course.objects.filter(major=Majors.phys,
                                                catalogNumber='406').get()


# Unity functions: create it all (to create db), fetch it all (for playing around)
def createAll() -> None:
    Semesters.create()
    Majors.create()
    Courses.create()


def fetchAll() -> None:
    Semesters.fetch()
    Majors.fetch()
    Courses.fetch()
