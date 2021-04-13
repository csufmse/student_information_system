from datetime import datetime

from django.test import TestCase

from sis.models import Semester
from sis.tests.utils import *


class AdminSemesterViewsExist(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(AdminSemesterViewsExist, cls).setUpTestData()

        createAdmin(username='u1', password='hello')
        createSemester()

    # list view
    def test_semesters_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/semesters'), 200)

    # single-object view
    def test_semester_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/semester/1'), 200)

    # edit view
    def test_edit_semesters_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/semester/1/edit'), 200)

    # create view
    def test_new_semesters_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/semester_new'), 200)

    # create view
    def test_semester_section_new_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/semester/1/section_new'), 200)


class AdminSemesterViewsTemplate(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(AdminSemesterViewsTemplate, cls).setUpTestData()

        createAdmin(username='u1', password='hello')
        createSemester()

    # list view
    def test_semesters_view_exists(self):
        self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semesters')
        self.assertTemplateUsed(response, 'schooladmin/semesters.html')

    # single-object view
    def test_semester_view_exists(self):
        self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semester/1')
        self.assertTemplateUsed(response, 'schooladmin/semester.html')

    # edit view
    def test_edit_semesters_view_exists(self):
        self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semester/1/edit')
        self.assertTemplateUsed(response, 'schooladmin/semester_edit.html')

    # create view
    def test_new_semesters_view_exists(self):
        self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semester_new')
        self.assertTemplateUsed(response, 'schooladmin/semester_new.html')

    # create view
    def test_semester_section_new_view_exists(self):
        self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/semester/1/section_new')
        self.assertTemplateUsed(response, 'schooladmin/section_new.html')
