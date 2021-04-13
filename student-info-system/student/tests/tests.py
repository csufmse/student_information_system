from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, SemesterStudent, Student, UpperField, ReferenceItem,
                        SectionReferenceItem)

from sis.tests.utils import *


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


class ViewsExist(TestCase):

    @classmethod
    def setUpTestData(cls):
        KLASS = ViewsExist
        super(KLASS, cls).setUpTestData()
        ad = createAdmin('foobar').profile
        m1 = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        KLASS.m = m1
        s = createStudent(username='u1', password='hello', major=m1)
        p = createProfessor(username='p1', password='hello', major=m1)
        c = createCourse(major=m1, num=101)
        ri = ReferenceItem.objects.create(professor=p, course=c, title='title')
        KLASS.sem = createSemester()
        KLASS.sec = Section.objects.create(semester=KLASS.sem,
                                           course=c,
                                           location='x',
                                           hours='24',
                                           professor=p)
        KLASS.sec.refresh_reference_items()
        KLASS.secstud = SectionStudent.objects.create(section=KLASS.sec, student=s)

    def current_schedule(self):
        self.assertEqual(self.simple('/current_schedule'), 200)

    def registration(self):
        self.assertEqual(self.simple('/registration'), 200)

    def profile_edit(self):
        self.assertEqual(self.simple('/profile/edit'), 200)

    def profile(self):
        self.assertEqual(self.simple('/profile'), 200)

    def change_password(self):
        self.assertEqual(self.simple('/change_password'), 200)

    def course(self):
        self.assertEqual(self.simple('/course/1'), 200)

    def drop(self):
        KLASS = self.__class__
        self.assertEqual(self.simple(f'/drop/{KLASS.secstud.id}'), 200)

    def user(self):
        self.assertEqual(self.simple('/user/1'), 200)

    def sectionstudent(self):
        KLASS = self.__class__
        self.assertEqual(self.simple(f'/sectionstudent/{KLASS.secstud.id}'), 200)

    def section(self):
        KLASS = self.__class__
        self.assertEqual(self.simple(f'/section/{KLASS.sec.id}'), 200)

    def semester(self):
        KLASS = self.__class__
        self.assertEqual(self.simple(f'/semester/{KLASS.sem.id}'), 200)

    def secitems(self):
        self.assertEqual(self.simple('/secitems'), 200)

    def secitem(self):
        KLASS = self.__class__
        sri = KLASS.sec.sectionreferenceitem_set.all()[0]
        self.assertEqual(self.simple(f'/secitem/{sri.id}'), 200)

    def major(self):
        KLASS = self.__class__
        self.assertEqual(self.simple(f'/section/{KLASS.m.id}'), 200)

    def history(self):
        self.assertEqual(self.simple('/history'), 200)

    # test methods can't start with "test"
    def xtest_majors(self):
        self.assertEqual(self.simple('/test_majors'), 200)

    def request_major_change(self):
        self.assertEqual(self.simple('/request_major_change'), 200)


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
