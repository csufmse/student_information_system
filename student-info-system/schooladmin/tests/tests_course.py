from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, SemesterStudent, Student, UpperField)

from sis.tests.utils import (createAdmin, createStudent, createProfessor, createCourse)


class AdminCoursesViewsTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = createAdmin(username='testuser1', password='hello')

    @classmethod
    def setUpTestData(self):
        ad = createAdmin('foobar').profile
        major = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_registration_closes=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           session=Semester.FALL,
                                           year=2000)

    # list views
    def test_courses_view_exists(self):
        login = self.client.login(username='testuser1', password='hello')
        response = self.client.get('/schooladmin/courses')
        self.assertEqual(response.status_code, 200)

    # single-object views
    def test_course_view_exists(self):
        login = self.client.login(username='testuser1', password='hello')
        response = self.client.get('/schooladmin/course/1')
        self.assertEqual(response.status_code, 200)

    # edit views
    def test_edit_course_view_exists(self):
        login = self.client.login(username='testuser1', password='hello')
        response = self.client.get('/schooladmin/course/1/edit')
        self.assertEqual(response.status_code, 200)

    def test_edit_course_view_uses_template(self):
        login = self.client.login(username='testuser1', password='hello')
        response = self.client.get('/schooladmin/course/1/edit')
        self.assertTemplateUsed(response, 'schooladmin/course_edit.html')

    # create views
    def test_new_course_view_exists(self):
        login = self.client.login(username='testuser1', password='hello')
        response = self.client.get('/schooladmin/course_new')
        self.assertEqual(response.status_code, 200)

    # misc
    def test_course_new_section_exists(self):
        login = self.client.login(username='testuser1', password='hello')
        response = self.client.get('/schooladmin/course/1/section_new')
        self.assertEqual(response.status_code, 200)


class Admin_Course_edit(TestCase):

    @classmethod
    def setUpTestData(cls):
        Admin_Course_edit.u1 = createAdmin('admin')
        major = Major.objects.create(abbreviation="CPSC",
                                     title="Computer Science",
                                     contact=Admin_Course_edit.u1.profile)
        Admin_Course_edit.c1 = createCourse(major, 101)

    def test_edit_course_view_template(self):
        login = self.client.login(username='admin', password='admin1')
        response = self.client.get('/schooladmin/course/1/edit')
        self.assertEqual(str(response.context['user']), 'admin')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schooladmin/course_edit.html')
