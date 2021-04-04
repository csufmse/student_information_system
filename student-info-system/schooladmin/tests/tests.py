from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Admin, Course, CoursePrerequisite, Major, Professor, Section,
                        SectionStudent, Semester, SemesterStudent, Student, TranscriptRequest,
                        UpperField)

from sis.tests.utils import createCourse, createAdmin, createStudent, createProfessor


class AdminViewsAccess(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(AdminViewsAccess, cls).setUpTestData()
        m1 = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        AdminViewsAccess.u1 = User.objects.create_user(username='u1', password='hello')
        Admin.objects.create(user=AdminViewsAccess.u1)
        AdminViewsAccess.u2 = User.objects.create_user(username='u2', password='hello')
        Professor.objects.create(user=AdminViewsAccess.u2, major=m1)
        AdminViewsAccess.u3 = User.objects.create_user(username='u3', password='hello')
        Student.objects.create(user=AdminViewsAccess.u3, major=m1)

    # list views
    def test_home_view_exists_for_admin(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/')
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'u1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schooladmin/home_admin.html')

    def test_home_view_redirects_for_prof(self):
        login = self.client.login(username='u2', password='hello')
        response = self.client.get('/schooladmin/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirects_for_stud(self):
        login = self.client.login(username='u3', password='hello')
        response = self.client.get('/schooladmin/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirect_login_for_loser(self):
        response = self.client.get('/schooladmin/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_login_for_loser(self):
        response = self.client.get('/schooladmin/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')


class AdminUserViewsTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<23fwd+tuK')
        test_user1.save()
        admin = Admin.objects.create(user=test_user1)
        admin.save()

    # list views
    def test_users_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/users')
        self.assertEqual(response.status_code, 200)

    # single-object views
    def test_user_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/user/1')
        self.assertEqual(response.status_code, 200)

    # edit views
    def test_edit_user_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/user/1/edit')
        self.assertEqual(response.status_code, 200)

    # create views
    def test_new_user_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/user_new')
        self.assertEqual(response.status_code, 200)

    # misc
    def test_user_pass_change_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/user/1/change_password')
        self.assertEqual(response.status_code, 200)
