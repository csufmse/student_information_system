from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from .models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                     Semester, Student, TranscriptRequest, UpperField)


def createStudent(major=None, username=None):
    user = User.objects.create(username=username, first_name=username[0], last_name=username[1:])
    stud = Student.objects.create(user=user, major=major)
    return stud


def createProfessor(major=None, username=None):
    user = User.objects.create(username=username, first_name=username[0], last_name=username[1:])
    prof = Professor.objects.create(user=user, major=major)
    return prof


class StudentTestCase_Basic(TestCase):

    @classmethod
    def setUpTestData(self):
        m = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        StudentTestCase_Basic.major = m

        StudentTestCase_Basic.stud = createStudent(major=m, username='testUser')

        StudentTestCase_Basic.c1 = Course.objects.create(major=m,
                                                         catalog_number='101',
                                                         title="required by major",
                                                         credits_earned=3.0)
        StudentTestCase_Basic.c2 = Course.objects.create(major=m,
                                                         catalog_number='102',
                                                         title="required by major",
                                                         credits_earned=3.0)

        StudentTestCase_Basic.semester = Semester.objects.create(
            date_registration_opens=datetime.now(),
            date_started=datetime.now(),
            date_last_drop=datetime.now(),
            date_ended=datetime.now(),
            semester='FA',
            year=2000)

    def test_class_level(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.class_level(), 'Freshman')

    def test_gpa(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.gpa(), 0.0)

    def test_credits_earned(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.credits_earned(), 0)

    def test_major(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.major, StudentTestCase_Basic.major)

    def test_name(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.name, 't estUser')

    def test_semesters(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.semesters.count(), 0)

    def test_sections(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.sections.count(), 0)

    def test_history(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.course_history().count(), 0)

    def test_remaining_required(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.remaining_required_courses().count(), 0)


class StudentTestCase_History(TestCase):

    @classmethod
    def setUpTestData(self):
        m = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        StudentTestCase_History.major = m

        StudentTestCase_History.stud = createStudent(major=m, username='testUser')
        p = createProfessor(major=m, username='tprof1')

        m_eng = Major.objects.create(abbreviation="ENGL", name="English")

        StudentTestCase_History.c1 = Course.objects.create(major=m,
                                                           catalog_number='101',
                                                           title="required by major",
                                                           credits_earned=3.0)
        StudentTestCase_History.c2 = Course.objects.create(major=m,
                                                           catalog_number='102',
                                                           title="required by major",
                                                           credits_earned=2.0)
        StudentTestCase_History.c3 = Course.objects.create(major=m,
                                                           catalog_number='103',
                                                           title="required by major",
                                                           credits_earned=6.0)
        StudentTestCase_History.c4 = Course.objects.create(major=m,
                                                           catalog_number='104',
                                                           title="not required by major",
                                                           credits_earned=2.0)
        StudentTestCase_History.e1 = Course.objects.create(major=m_eng,
                                                           catalog_number='218',
                                                           title="required by CPSC 104",
                                                           credits_earned=3.0)
        StudentTestCase_History.e2 = Course.objects.create(major=m_eng,
                                                           catalog_number='300',
                                                           title="required by CPSC 102",
                                                           credits_earned=3.0)

        # set up required by major
        m.courses_required.add(StudentTestCase_History.c1, StudentTestCase_History.c2,
                               StudentTestCase_History.c3)
        m.save()

        # set up course prereqs
        CoursePrerequisite.objects.create(course=StudentTestCase_History.c2,
                                          prerequisite=StudentTestCase_History.e2)
        CoursePrerequisite.objects.create(course=StudentTestCase_History.c4,
                                          prerequisite=StudentTestCase_History.e1)

        StudentTestCase_History.semester = Semester.objects.create(
            date_registration_opens=datetime.now(),
            date_started=datetime.now(),
            date_last_drop=datetime.now(),
            date_ended=datetime.now(),
            semester='FA',
            year=2000)

        StudentTestCase_History.stud.semesters.add(StudentTestCase_History.semester)
        StudentTestCase_History.stud.save()

        StudentTestCase_History.sec1 = Section.objects.create(
            course=StudentTestCase_History.c1,
            semester=StudentTestCase_History.semester,
            professor=p)
        StudentTestCase_History.sec2 = Section.objects.create(
            course=StudentTestCase_History.c2,
            semester=StudentTestCase_History.semester,
            professor=p)
        StudentTestCase_History.sec3 = Section.objects.create(
            course=StudentTestCase_History.c3,
            semester=StudentTestCase_History.semester,
            professor=p)
        StudentTestCase_History.sec4 = Section.objects.create(
            course=StudentTestCase_History.e2,
            semester=StudentTestCase_History.semester,
            professor=p)
        StudentTestCase_History.studsec1 = SectionStudent.objects.create(
            section=StudentTestCase_History.sec1,
            student=StudentTestCase_History.stud,
            status=SectionStudent.GRADED,
            grade=SectionStudent.GRADE_B)
        StudentTestCase_History.studsec2 = SectionStudent.objects.create(
            section=StudentTestCase_History.sec2,
            student=StudentTestCase_History.stud,
            status=SectionStudent.GRADED,
            grade=SectionStudent.GRADE_F)
        StudentTestCase_History.studsec3 = SectionStudent.objects.create(
            section=StudentTestCase_History.sec3,
            student=StudentTestCase_History.stud,
            status=SectionStudent.DROPPED)
        StudentTestCase_History.studsec4 = SectionStudent.objects.create(
            section=StudentTestCase_History.sec4,
            student=StudentTestCase_History.stud,
            status=SectionStudent.GRADED,
            grade=SectionStudent.GRADE_C)
        # c1: required, passed (B)
        # c2: required, failed
        # c3: required, (DROPPED)
        # c4: not required, not taken
        # e1: a prereq of c4
        # e2: a prereq of c2

    def test_gpa(self):
        student = (User.objects.get(username="testUser")).student
        self.assertEqual(student.gpa(), (3 * 3.0 + 0 * 2.0 + 2 * 3.0) / (3.0 + 2.0 + 3.0))

    def test_semesters(self):
        student = StudentTestCase_History.stud
        self.assertEqual(student.semesters.count(), 1)

    def test_history_all(self):
        student = StudentTestCase_History.stud
        history = student.course_history()
        self.assertEqual(history.count(), 4)
        self.assertEqual(history[0].section, StudentTestCase_History.sec1)
        self.assertEqual(history[1].section, StudentTestCase_History.sec2)
        self.assertEqual(history[2].section, StudentTestCase_History.sec3)
        self.assertEqual(history[3].section, StudentTestCase_History.sec4)

    def test_history_passed(self):
        student = StudentTestCase_History.stud
        history = student.course_history(passed=True)
        self.assertEqual(history.count(), 2)
        self.assertEqual(history[0].section, StudentTestCase_History.sec1)
        self.assertEqual(history[1].section, StudentTestCase_History.sec4)

    def test_history_graded(self):
        student = StudentTestCase_History.stud
        history = student.course_history(graded=True)
        self.assertEqual(history.count(), 3)
        self.assertEqual(history[0].section, StudentTestCase_History.sec1)
        self.assertEqual(history[1].section, StudentTestCase_History.sec2)
        self.assertEqual(history[2].section, StudentTestCase_History.sec4)

    def test_history_required(self):
        student = StudentTestCase_History.stud
        history = student.course_history(required=True)
        self.assertEqual(history.count(), 3)
        self.assertEqual(history[0].section, StudentTestCase_History.sec1)
        self.assertEqual(history[1].section, StudentTestCase_History.sec2)
        self.assertEqual(history[2].section, StudentTestCase_History.sec3)

    def test_history_prereqs_not_fulfilled(self):
        student = StudentTestCase_History.stud
        history = student.course_history(prereqs_for=StudentTestCase_History.c4)
        self.assertEqual(history.count(), 0)

    def test_history_prereqs_fulfilled(self):
        student = StudentTestCase_History.stud
        history = student.course_history(prereqs_for=StudentTestCase_History.c2)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history[0].section, StudentTestCase_History.sec4)

    def test_credits_earned(self):
        student = StudentTestCase_History.stud
        self.assertEqual(student.credits_earned(), 3.0 + 3.0)

    def test_remaining_required(self):
        student = StudentTestCase_History.stud
        rem = student.remaining_required_courses()
        self.assertEqual(rem.count(), 2)
        self.assertEqual(rem[0], StudentTestCase_History.c2)
        self.assertEqual(rem[1], StudentTestCase_History.c3)


class ProfessorTestCase(TestCase):

    def setUp(self):
        User.objects.create(username="prof", first_name="First", last_name="Last")

    def test_professor_name(self):
        user = User.objects.get(username="prof")
        professor = Professor.objects.create(user=user)
        self.assertEqual(professor.name, "First Last")


class CourseTestCase(TestCase):

    def setUp(self):
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        Course.objects.create(major=major,
                              catalog_number='101',
                              title="Intro To Test",
                              credits_earned=3.0)

    def test_course_major_name(self):
        course = Course.objects.get(title="Intro To Test")
        self.assertEqual(course.major_name, "Computer Science")

    def test_course_name(self):
        course = Course.objects.get(title="Intro To Test")
        self.assertEqual(course.name, "CPSC-101")


class SectionTestCase(TestCase):

    @classmethod
    def setUpTestData(self):
        user = User.objects.create(username="prof", first_name="First", last_name="Last")
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        professor = Professor.objects.create(user=user)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           semester='FA',
                                           year=2000)
        Section.objects.create(course=course,
                               professor=professor,
                               semester=semester,
                               number=1,
                               hours="MW 1200-1400")

    def test_section_course_name(self):
        section = Section.objects.get(hours="MW 1200-1400")
        self.assertEqual(section.course_name, "CPSC-101")

    def test_section_professor_name(self):
        section = Section.objects.get(hours="MW 1200-1400")
        self.assertEqual(section.professor_name, "First Last")

    def test_section_semester_name(self):
        section = Section.objects.get(hours="MW 1200-1400")
        self.assertEqual(section.semester_name, "FA-2000")

    def test_section_name(self):
        section = Section.objects.get(hours="MW 1200-1400")
        self.assertEqual(section.name, "CPSC-101-1")
