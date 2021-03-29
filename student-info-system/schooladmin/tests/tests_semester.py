from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Admin, Course, CoursePrerequisite, Major, Professor, Section,
                        SectionStudent, Semester, SemesterStudent, Student, TranscriptRequest,
                        UpperField)


class AdminSemesterViewsTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<23fwd+tuK')
        test_user1.save()
        admin = Admin.objects.create(user=test_user1)
        admin.save()

    @classmethod
    def setUpTestData(self):
        user_p = User.objects.create(username="prof", first_name="First", last_name="Last")
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        professor = Professor.objects.create(user=user_p, major=major)
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
        user_s = User.objects.create(username="stud", first_name="First", last_name="Last")
        self.student = Student.objects.create(user=user_s, major=major)
        SectionStudent.objects.create(student=self.student, section=section)

    # list views
    def test_semesters_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/semesters')
        self.assertEqual(response.status_code, 200)

    # single-object views
    def test_semester_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/semester/1')
        self.assertEqual(response.status_code, 200)

    # edit views
    def test_edit_semesters_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/semester/1/edit')
        self.assertEqual(response.status_code, 200)

    # create views
    def test_new_semesters_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/semester_new')
        self.assertEqual(response.status_code, 200)

    # create views
    def test_semester_section_new_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/semester/1/section_new')
        self.assertEqual(response.status_code, 200)
