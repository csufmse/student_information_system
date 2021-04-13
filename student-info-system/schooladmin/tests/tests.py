from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, SemesterStudent, Student, UpperField)

from sis.tests.utils import createCourse, createAdmin, createStudent, createProfessor


class AdminViewsAccess(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(AdminViewsAccess, cls).setUpTestData()
        ad = createAdmin('foobar').profile
        m1 = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        AdminViewsAccess.u1 = createAdmin(username='u1', password='hello')
        AdminViewsAccess.u2 = createProfessor(username='u2', password='hello', major=m1)
        AdminViewsAccess.u3 = createStudent(username='u3', password='hello', major=m1)

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

    @classmethod
    def setUpTestData(cls):
        super(AdminUserViewsTest, cls).setUpTestData()
        createAdmin(username='u1', password='hello')

    # list views
    def test_users_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/users'), 200)

    # single-object views
    def test_user_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/user/1'), 200)

    # edit views
    def test_edit_user_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/user/1/edit'), 200)

    # create views
    def test_new_user_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/user_new'), 200)

    # misc
    def test_user_pass_change_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/user/1/change_password'), 200)
