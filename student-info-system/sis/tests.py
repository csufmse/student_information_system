from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from .models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                     Semester, Student, TranscriptRequest, UpperField)


class StudentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(StudentTestCase, cls).setUpTestData()

        StudentTestCase.major = Major.objects.create(abbreviation="CPSC", name="Computer Science")

        StudentTestCase.u_stud = User.objects.create(username="testUser", first_name="First", last_name="Last")
        StudentTestCase.stud = Student.objects.create(user=StudentTestCase.u_stud, major=StudentTestCase.major)

        StudentTestCase.u_prof = User.objects.create(username="prof", first_name="First", last_name="Last")
        StudentTestCase.prof = Professor.objects.create(user=StudentTestCase.u_prof, major=StudentTestCase.major)

        StudentTestCase.sem = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           semester='FA',
                                           year=2000)

        StudentTestCase.stud.semesters.add(StudentTestCase.sem)
        StudentTestCase.stud.save()

        StudentTestCase.c1 = Course.objects.create(major=StudentTestCase.major,
                                                   catalog_number='101',
                                                   title="Intro To Test",
                                                   credits_earned=3.0)

        StudentTestCase.s1 = Section.objects.create(course=StudentTestCase.c1,
                                                    professor=StudentTestCase.prof,
                                                    semester=StudentTestCase.sem,
                                                    number=1,
                                                    hours="MW 1200-1400")

        StudentTestCase.c2 = Course.objects.create(major=StudentTestCase.major,
                                                   catalog_number='110',
                                                   title="Testing",
                                                   credits_earned=3.0)

        StudentTestCase.s2 = Section.objects.create(course=StudentTestCase.c2,
                                                    professor=StudentTestCase.prof,
                                                    semester=StudentTestCase.sem,
                                                    number=1,
                                                    hours="WF 0900-0930")

        StudentTestCase.ss1 = SectionStudent.objects.create(student=StudentTestCase.stud,
                           section=StudentTestCase.s1,
                           grade=None,
                           status=SectionStudent.REGISTERED)


    def test_class_level(self):
        student = (User.objects.get(username="testUser")).student
        self.assertEqual(student.class_level(), 'Freshman')

    def test_gpa(self):
        student = (User.objects.get(username="testUser")).student
        self.assertEqual(student.gpa(), 0.0)

    def test_student_name(self):
        student = (User.objects.get(username="testUser")).student
        self.assertEqual(student.name, 'First Last')

    def test_required_order(self):
        u2 = User.objects.create(username="abolio", first_name="f", last_name="l")
        s2 = Student.objects.create(user=u2, major=StudentTestCase.major)

        u3 = User.objects.create(username="yot", first_name="qwer", last_name="want")
        s3 = Student.objects.create(user=u3, major=StudentTestCase.major)

        studs = Student.objects.all()
        self.assertEqual(Student.objects.all()[0].user.username, 'abolio')
        self.assertEqual(Student.objects.all()[1].user.username, 'testUser')
        self.assertEqual(Student.objects.all()[2].user.username, 'yot')

    def test_gpa_after_grading(self):
        StudentTestCase.ss1.grade = SectionStudent.GRADE_B
        StudentTestCase.ss1.status = SectionStudent.GRADED
        StudentTestCase.ss1.save()
        student = Student.objects.get(user__username="testUser")
        self.assertEqual(student.gpa(), 3.0)



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
    def setUpTestData(cls):
        super(SectionTestCase, cls).setUpTestData()
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

class MajorTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(MajorTestCase, cls).setUpTestData()
        MajorTestCase.m1 = Major.objects.create(abbreviation="CPSC",
                                                      name="Computer Science")
        MajorTestCase.c1 = Course.objects.create(major=MajorTestCase.m1,
                                                       catalog_number='400',
                                                       title="ZZZ Intro To Test",
                                                       credits_earned=3.0)
        MajorTestCase.c2 = Course.objects.create(major=MajorTestCase.m1,
                                                       catalog_number='300',
                                                       title="AAA More Test",
                                                       credits_earned=3.0)
        MajorTestCase.c3 = Course.objects.create(major=MajorTestCase.m1,
                                                       catalog_number='350',
                                                       title="PPP Still More",
                                                       credits_earned=3.0)
        MajorTestCase.m1.courses_required.add(MajorTestCase.c1)
        MajorTestCase.m1.courses_required.add(MajorTestCase.c2)
        MajorTestCase.m1.courses_required.add(MajorTestCase.c3)
        MajorTestCase.m1.save()

    def test_major_abbrev(self):
        m = Major.objects.get(name='Computer Science')
        self.assertEqual(m.abbreviation, "CPSC")

    def test_major_name(self):
        m = Major.objects.get(abbreviation='CPSC')
        self.assertEqual(m.name, "Computer Science")

    def test_required_order(self):
        m = Major.objects.get(abbreviation='CPSC')
        self.assertEqual(m.courses_required.count(), 3)
        self.assertEqual(m.courses_required.all()[0].catalog_number, '300')
        self.assertEqual(m.courses_required.all()[1].catalog_number, '350')
        self.assertEqual(m.courses_required.all()[2].catalog_number, '400')

