from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from .models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                     Semester, Student, TranscriptRequest, UpperField)


class StudentTestCase(TestCase):

    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create(username="testUser", first_name="First", last_name="Last")
        user_p = User.objects.create(username="prof", first_name="First", last_name="Last")
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        professor = Professor.objects.create(user=user_p)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           semester='FA',
                                           year=2000)
        section = Section.objects.create(course=course,
                                         professor=professor,
                                         semester=semester,
                                         number=1,
                                         hours="MW 1200-1400")
        self.student = Student.objects.create(user=self.user, major=major)
        self.student.sections.add(section)

    def test_class_level(self):
        student = (User.objects.get(username="testUser")).student
        self.assertEqual(student.class_level(), 'Freshman')

    def test_gpa(self):
        student = (User.objects.get(username="testUser")).student
        self.assertEqual(student.gpa(), 0.0)

    def test_student_name(self):
        student = (User.objects.get(username="testUser")).student
        self.assertEqual(student.name, 'First Last')


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
