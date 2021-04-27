from django.test import TestCase

from sis.models import (
    Major,)
from sis.tests.utils import *


class ProfessorViewsAccess(TestCase):

    @classmethod
    def setUpTestData(cls):
        KLASS = ProfessorViewsAccess
        super(KLASS, cls).setUpTestData()
        ad = createAdmin('foobar').profile
        m1 = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        KLASS.u1 = createProfessor(username='u1', password='hello', major=m1)
        KLASS.u3 = createStudent(username='u3', password='hello', major=m1)

    # list views
    def test_home_view_exists_for_professor(self):
        self.client.login(username='u1', password='hello')
        response = self.client.get('/')
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'u1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'professor/home_professor.html')

    def test_home_view_redirects_for_stud(self):
        login = self.client.login(username='u3', password='hello')
        response = self.client.get('/professor/')
        self.assertEqual(response.status_code, 301)

    def test_home_view_redirect_login_for_loser(self):
        response = self.client.get('/professor/')
        self.assertEqual(response.status_code, 301)

    def test_home_view_login_for_loser(self):
        response = self.client.get('/professor/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schooladmin/home_guest.html')
