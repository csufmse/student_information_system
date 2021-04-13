from datetime import datetime

from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, SemesterStudent, Student, UpperField)

from sis.tests.utils import *


class AdminSectionViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(AdminSectionViewsTest, cls).setUpTestData()

        createAdmin(username='u1', password='hello')
        ad = createAdmin('foobar').profile
        major = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        professor = createProfessor(username="prof", major=major)
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        semester = createSemester()
        section = Section.objects.create(course=course,
                                         professor=professor,
                                         location="somewhere",
                                         semester=semester,
                                         number=1,
                                         hours="MW 1200-1400")
        stud = createStudent(username='stud', major=major)
        SectionStudent.objects.create(student=stud, section=section)

    # list views
    def test_sections_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/sections'), 200)

    # single-object views
    def test_section_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/section/1'), 200)

    # edit views
    def test_edit_section_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/section/1/edit'), 200)

    # create views
    def test_new_section_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/section_new'), 200)

    def test_section_new_from_section_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/section/1/new_from_section'), 200)
