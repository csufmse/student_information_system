from django.test import TestCase

from django.contrib.auth.models import User
from sis.models import (Admin, Course, CoursePrerequisite, Major, Professor, Section,
                        SectionStudent, Semester, SemesterStudent, Student, UpperField)


class ViewsAccess(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ViewsAccess, cls).setUpTestData()
        m1 = Major.objects.create(abbreviation="CPSC", title="Computer Science")
        ViewsAccess.u1 = User.objects.create_user(username='u1', password='hello')
        Admin.objects.create(user=ViewsAccess.u1)
        ViewsAccess.u2 = User.objects.create_user(username='u2', password='hello')
        Professor.objects.create(user=ViewsAccess.u2, major=m1)
        ViewsAccess.u3 = User.objects.create_user(username='u3', password='hello')
        Student.objects.create(user=ViewsAccess.u3, major=m1)

    def test_home_view_redirects_for_admin(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirects_for_prof(self):
        login = self.client.login(username='u2', password='hello')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirects_for_stud(self):
        login = self.client.login(username='u3', password='hello')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirect_login_for_loser(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_login_for_loser(self):
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')


class ViewsUseTemplate(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ViewsUseTemplate, cls).setUpTestData()
        m1 = Major.objects.create(abbreviation="CPSC", title="Computer Science")
        ViewsAccess.u = User.objects.create_user(username='u', password='hello')
        Student.objects.create(user=ViewsAccess.u, major=m1)

    def access_denied(self):
        login = self.client.login(username='u', password='hello')
        response = self.client.get('/access_denied')
        self.assertTemplateUsed(response, 'sis/access_denied.html')
