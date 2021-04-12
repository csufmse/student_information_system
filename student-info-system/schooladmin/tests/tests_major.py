from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, SemesterStudent, Student, UpperField)

from sis.tests.utils import (createStudent, createProfessor, createAdmin, createCourse)


class AdminMajorViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(AdminMajorViewsTest, cls).setUpTestData()
        AdminMajorViewsTest.test_user1 = createAdmin(username='testuser1')
        AdminMajorViewsTest.m1 = Major.objects.create(
            abbreviation="CPSC",
            title="Computer Science",
            contact=AdminMajorViewsTest.test_user1.profile)
        AdminMajorViewsTest.m2 = Major.objects.create(
            abbreviation="ENGL", title="English", contact=AdminMajorViewsTest.test_user1.profile)
        AdminMajorViewsTest.m3 = Major.objects.create(
            abbreviation="LIT",
            title="Literature",
            contact=AdminMajorViewsTest.test_user1.profile)
        AdminMajorViewsTest.c1 = Course.objects.create(major=AdminMajorViewsTest.m1,
                                                       catalog_number='101',
                                                       title="Intro To Test",
                                                       credits_earned=3.0)
        AdminMajorViewsTest.c2 = Course.objects.create(major=AdminMajorViewsTest.m1,
                                                       catalog_number='102',
                                                       title="More Test",
                                                       credits_earned=3.0)
        AdminMajorViewsTest.c3 = Course.objects.create(major=AdminMajorViewsTest.m3,
                                                       catalog_number='101',
                                                       title="something else",
                                                       credits_earned=3.0)
        AdminMajorViewsTest.m1.courses_required.add(AdminMajorViewsTest.c1)
        AdminMajorViewsTest.m1.courses_required.add(AdminMajorViewsTest.c3)
        AdminMajorViewsTest.m1.save()

    def test_majors_view_exists(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/majors')
        self.assertEqual(response.status_code, 200)

    def test_majors_view_uses_template(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/majors')
        self.assertTemplateUsed(response, 'schooladmin/majors.html')

    # single-object views
    def test_major_view_exists(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/major/' + str(AdminMajorViewsTest.m1.id))
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_major_fails_view(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/major/' + '445455554')
        self.assertEqual(response.status_code, 404)

    def test_major_view_uses_template(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/major/' + str(AdminMajorViewsTest.m1.id))
        self.assertTemplateUsed(response, 'schooladmin/major.html')

    # edit views
    def test_edit_major_view_exists(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/major/' + str(AdminMajorViewsTest.m1.id) +
                                   '/edit')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schooladmin/major_edit.html')

    # create views
    def test_new_major_view_exists(self):
        login = self.client.login(username='testuser1', password='testuser11')
        response = self.client.get('/schooladmin/major_new')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schooladmin/major_new.html')
