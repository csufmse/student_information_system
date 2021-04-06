from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, SemesterStudent, Student, UpperField)

from sis.tests.utils import (createStudent, createProfessor, createAdmin, createCourse)


class AdminSectionViewsTest(TestCase):

    def setUp(self):
        test_user1 = createAdmin(username='testuser1')

    @classmethod
    def setUpTestData(self):
        major = Major.objects.create(abbreviation="CPSC", title="Computer Science")
        professor = createProfessor(username="prof", major=major)
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_registration_closes=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           session=Semester.FALL,
                                           year=2000)
        section = Section.objects.create(course=course,
                                         professor=professor,
                                         location="somewhere",
                                         semester=semester,
                                         number=1,
                                         hours="MW 1200-1400")
        self.student = createStudent(username='stud', major=major)
        SectionStudent.objects.create(student=self.student, section=section)

    # list views
    def test_sections_view_exists(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/sections')
        self.assertEqual(response.status_code, 200)

    # single-object views
    def test_section_view_exists(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/section/1')
        self.assertEqual(response.status_code, 200)

    # edit views
    def test_edit_section_view_exists(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/section/1/edit')
        self.assertEqual(response.status_code, 200)

    # create views
    def test_new_section_view_exists(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/section_new')
        self.assertEqual(response.status_code, 200)

    def test_section_new_from_section_view_exists(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/section/1/new_from_section')
        self.assertEqual(response.status_code, 200)
