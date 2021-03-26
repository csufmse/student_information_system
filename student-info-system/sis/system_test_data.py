from datetime import date

from django.contrib.auth.models import User

from .models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                     Semester, Student, TranscriptRequest)

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
#   2. Add the model to create_all() and fetch_all()
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
#   7. create_all()
#
# How to use this to play around in the shell:
#   (basically a fast way to access created objects)
#   1. manage.py shell
#   2. from sis.system_test_data import *
#   3. fetch_all()
#   3.5. If you only need one Models's worth do it directly: Majors.fetch_all()
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
        Majors.cpsc = Major(abbreviation='CPSC',
                            name="Computer Science",
                            description="bits and byte, oh my!")
        Majors.cpsc.save()
        Majors.engl = Major(abbreviation='ENGL',
                            name='English',
                            description='Composition, Literature, and Rhetoric. Not Grunting.')
        Majors.engl.save()
        Majors.arch = Major(abbreviation='ARCH',
                            name='Architecture',
                            description='Buildings and Ditches')
        Majors.arch.save()
        Majors.phys = Major(abbreviation='PHYS', name='Physics', description='Why Things Break')
        Majors.phys.save()

    @classmethod
    def fetch(cls) -> None:
        Majors.cpsc = Major.objects.filter(abbreviation='CPSC').get()
        Majors.phys = Major.objects.filter(abbreviation='PHYS').get()
        Majors.arch = Major.objects.filter(abbreviation='ARCH').get()
        Majors.engl = Major.objects.filter(abbreviation='ENGL').get()


class Courses():

    @classmethod
    def create(cls) -> None:
        Courses.cpsc101 = Course(major=Majors.cpsc,
                                 catalog_number='101',
                                 title='Intro to Programming',
                                 credits_earned=3.0)
        Courses.cpsc101.save()
        Courses.cpsc345 = Course(major=Majors.cpsc,
                                 catalog_number='345',
                                 title='Data Structures',
                                 credits_earned=3.0)
        Courses.cpsc345.save()
        Courses.engl218 = Course(major=Majors.engl,
                                 catalog_number='218',
                                 title='Technical Writing',
                                 credits_earned=3.0)
        Courses.engl218.save()
        Courses.engl255 = Course(major=Majors.engl,
                                 catalog_number='255',
                                 title='Bible as Literature',
                                 credits_earned=3.0)
        Courses.engl255.save()
        Courses.phys405 = Course(major=Majors.phys,
                                 catalog_number='405',
                                 title='Quantum Mechanics',
                                 credits_earned=4.0)
        Courses.phys405.save()
        Courses.phys406 = Course(major=Majors.phys,
                                 catalog_number='406',
                                 title='Advanced Quantum Mechanics',
                                 credits_earned=4.0)
        Courses.phys406.save()

    @classmethod
    def fetch(cls) -> None:
        Majors.fetch()
        Courses.cpsc101 = Course.objects.filter(major=Majors.cpsc, catalog_number='101').get()
        Courses.cpsc345 = Course.objects.filter(major=Majors.cpsc, catalog_number='345').get()
        Courses.engl218 = Course.objects.filter(major=Majors.engl, catalog_number='218').get()
        Courses.engl255 = Course.objects.filter(major=Majors.engl, catalog_number='255').get()
        Courses.phys405 = Course.objects.filter(major=Majors.phys, catalog_number='405').get()
        Courses.phys406 = Course.objects.filter(major=Majors.phys, catalog_number='406').get()


class Professors():

    @classmethod
    def create(cls) -> None:
        u = User(username='bjmckenz_prof', first_name='bpfn', last_name='bpln')
        u.save()
        professor = Professor.objects.create(user=user)
        Professors.bjm = Professor(user_id=u.id, major_id=Majors.cpsc)
        Professors.bjm.save()

    @classmethod
    def fetch(cls) -> None:
        Professors.bjm = Professor.objects.filter(user__username='bjmckenz_prof').get()


class CoursePrerequisites():

    @classmethod
    def create(cls) -> None:
        CoursePrerequisites.e218e255 = CoursePrerequisite(course=Courses.engl255,
                                                          prerequisite=Courses.engl218)
        CoursePrerequisites.e218e255.save()
        CoursePrerequisites.c101c345 = CoursePrerequisite(course=Courses.cpsc345,
                                                          prerequisite=Courses.cpsc101)
        CoursePrerequisites.c101c345.save()

    @classmethod
    def fetch(cls) -> None:
        CoursePrerequisites.e218e255 = CoursePrerequisite.objects.filter(
            prerequisite=Courses.engl218).get()
        CoursePrerequisites.c101c345 = CoursePrerequisite.objects.filter(
            prerequisite=Courses.cpsc101).get()


# Unity functions: create it all (to create db), fetch it all (for playing around)
def create_all() -> None:
    Semesters.create()
    Majors.create()
    Courses.create()
    Professors.create()
    CoursePrerequisites.create()


def fetch_all() -> None:
    Semesters.fetch()
    Majors.fetch()
    Courses.fetch()
    Professors.fetch()
    CoursePrerequisites.fetch()
