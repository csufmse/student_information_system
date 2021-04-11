from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, SemesterStudent, Student, UpperField)

from sis.tests.utils import (createStudent, createProfessor, createAdmin, createCourse)


class ViewsAccess(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ViewsAccess, cls).setUpTestData()
        ad = createAdmin('foobar').profile
        m1 = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        ViewsAccess.u1 = createAdmin(username='u1', password='hello')
        ViewsAccess.u2 = createProfessor(username='u2', password='hello', major=m1)
        ViewsAccess.u3 = createStudent(username='u3', password='hello', major=m1)

    def test_home_view_redirects_for_admin(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirects_for_prof(self):
        login = self.client.login(username='u2', password='hello')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_exists_for_stud(self):
        login = self.client.login(username='u3', password='hello')
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['user']), 'u3')

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
        ViewsAccess.u = createStudent(username='u', password='hello', major=m1)

    def current_schedule(self):
        login = self.client.login(username='u', password='hello')
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'student/current_schedule.html')

    def registration(self):
        login = self.client.login(username='u', password='hello')
        response = self.client.get('/registration')
        self.assertTemplateUsed(response, 'student/registration.html')
