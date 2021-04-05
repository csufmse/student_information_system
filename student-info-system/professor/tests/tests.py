from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Admin, Course, CoursePrerequisite, Major, Professor, Section,
                        SectionStudent, Semester, SemesterStudent, Student, UpperField)


class ProfessorViewsAccess(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ProfessorViewsAccess, cls).setUpTestData()
        m1 = Major.objects.create(abbreviation="CPSC", title="Computer Science")
        ProfessorViewsAccess.u1 = User.objects.create_user(username='u1', password='hello')
        Professor.objects.create(user=ProfessorViewsAccess.u1)
        ProfessorViewsAccess.u2 = User.objects.create_user(username='u2', password='hello')
        Professor.objects.create(user=ProfessorViewsAccess.u2, major=m1)
        ProfessorViewsAccess.u3 = User.objects.create_user(username='u3', password='hello')
        Student.objects.create(user=ProfessorViewsAccess.u3, major=m1)

    # list views
    def test_home_view_exists_for_professor(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/professor/')
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'u1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'professor/home_professor.html')

    def test_home_view_redirects_for_stud(self):
        login = self.client.login(username='u3', password='hello')
        response = self.client.get('/professor/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirect_login_for_loser(self):
        response = self.client.get('/professor/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_login_for_loser(self):
        response = self.client.get('/professor/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
