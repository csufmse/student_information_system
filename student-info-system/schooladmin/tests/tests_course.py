from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, SemesterStudent, Student, UpperField)

from sis.tests.utils import *


class AdminCoursesViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(AdminCoursesViewsTest, cls).setUpTestData()
        createAdmin(username='u1', password='hello')
        ad = createAdmin('foobar').profile
        major = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        Course.objects.create(major=major,
                              catalog_number='101',
                              title="Intro To Test",
                              credits_earned=3.0)

    # list views
    def test_courses_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/courses'), 200)

    # single-object views
    def test_course_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/course/1'), 200)

    # edit views
    def test_edit_course_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/course/1/edit'), 200)

    def test_edit_course_view_uses_template(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/schooladmin/course/1/edit')
        self.assertTemplateUsed(response, 'schooladmin/course_edit.html')

    # create views
    def test_new_course_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/course_new'), 200)

    # misc
    def test_course_new_section_exists(self):
        self.assertEqual(self.simple('/schooladmin/course/1/section_new'), 200)


class Admin_Course_edit(TestCase):

    @classmethod
    def setUpTestData(cls):
        KLASS = Admin_Course_edit
        super(KLASS, cls).setUpTestData()
        KLASS.u1 = createAdmin('admin')
        major = Major.objects.create(abbreviation="CPSC",
                                     title="Computer Science",
                                     contact=KLASS.u1.profile)
        KLASS.c1 = createCourse(major, 101)

    def test_edit_course_view_template(self):
        self.client.login(username='admin', password='admin1')
        response = self.client.get('/schooladmin/course/1/edit')
        self.assertEqual(str(response.context['user']), 'admin')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schooladmin/course_edit.html')
