from django.test import TestCase

from sis.models import (
    Major,)

from sis.tests.utils import *


class ViewsAccess(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ViewsAccess, cls).setUpTestData()
        ad = createAdmin('foobar').profile
        m1 = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        createAdmin(username='u1', password='hello')
        createProfessor(username='u2', major=m1, password='hello')
        createStudent(username='u3', major=m1, password='hello')

    def test_home_view_redirects_for_admin(self):
        self.client.login(username='u1', password='hello')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirects_for_prof(self):
        self.client.login(username='u2', password='hello')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirects_for_stud(self):
        self.client.login(username='u3', password='hello')
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
        ad = createAdmin('foobar').profile
        m1 = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        createUser(username='u', password='hello', major=m1)

    def access_denied(self):
        self.client.login(username='u', password='hello')
        response = self.client.get('/access_denied')
        self.assertTemplateUsed(response, 'sis/access_denied.html')
