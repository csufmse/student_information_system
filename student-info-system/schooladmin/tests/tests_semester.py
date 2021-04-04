from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Admin, Course, CoursePrerequisite, Major, Professor, Section,
                        SectionStudent, Semester, SemesterStudent, Student, TranscriptRequest,
                        UpperField)


class AdminSemesterViewsExist(TestCase):

    @classmethod
    def setUpTestData(self):
        test_user1 = User.objects.create_user(username='u1', password='hello')
        admin = Admin.objects.create(user=test_user1)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           semester=Semester.FALL,
                                           year=2000)

    # list view
    def test_semesters_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semesters')
        self.assertEqual(response.status_code, 200)

    # single-object view
    def test_semester_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semester/1')
        self.assertEqual(response.status_code, 200)

    # edit view
    def test_edit_semesters_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semester/1/edit')
        self.assertEqual(response.status_code, 200)

    # create view
    def test_new_semesters_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semester_new')
        self.assertEqual(response.status_code, 200)

    # create view
    def test_semester_section_new_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semester/1/section_new')
        self.assertEqual(response.status_code, 200)


class AdminSemesterViewsTemplate(TestCase):

    @classmethod
    def setUpTestData(self):
        test_user1 = User.objects.create_user(username='u1', password='hello')
        admin = Admin.objects.create(user=test_user1)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           semester=Semester.FALL,
                                           year=2000)

    # list view
    def test_semesters_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semesters')
        self.assertTemplateUsed(response, 'schooladmin/semesters.html')

    # single-object view
    def test_semester_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semester/1')
        self.assertTemplateUsed(response, 'schooladmin/semester.html')

    # edit view
    # def test_edit_semesters_view_exists(self):
    #     login = self.client.login(username='u1', password='hello')
    #     response = self.client.get('/schooladmin/semester/1/edit')
    #     self.assertTemplateUsed(response, 'schooladmin/semester_edit.html')

    # create view
    # def test_new_semesters_view_exists(self):
    #     login = self.client.login(username='u1', password='hello')
    #     response = self.client.get('/schooladmin/semester_new')
    #     self.assertTemplateUsed(response, 'schooladmin/semester_new.html')

    # create view
    def test_semester_section_new_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semester/1/section_new')
        self.assertTemplateUsed(response, 'schooladmin/section_new.html')
