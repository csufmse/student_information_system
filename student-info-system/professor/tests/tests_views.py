from datetime import datetime
from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Profile, Section,
                        SectionStudent, Semester, SemesterStudent, Student, UpperField)
from sis.tests.utils import *


class ProfessorSectionViewsTest(TestCase):

    @classmethod
    def setUpTestData(self):
        ad = createAdmin('foobar').profile
        major = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        prof = createProfessor(username='u1', password='hello', major=major)
        createStudent(username='u2', password='hello', major=major)
        course = createCourse(major=major, num='101')
        semester = createSemester()
        Section.objects.create(course=course,
                               professor=prof,
                               semester=semester,
                               number=1,
                               hours="MW 1200-1400")

    # list views
    def test_sections_view_exists(self):
        self.assertEqual(self.simple('/professor/sections'), 200)

    def test_section_view_exists(self):
        self.assertEqual(self.simple('/professor/section/1/student'), 200)


class ProfessorSectionViewsTest(TestCase):

    @classmethod
    def setUpTestData(self):
        ad = createAdmin('foobar').profile
        major = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        prof = createProfessor(username='u1', password='hello', major=major)
        stud = createStudent(username='u2', password='hello', major=major)
        course = createCourse(major=major, num='101')
        semester = createSemester()
        section = Section.objects.create(course=course,
                                         professor=prof,
                                         semester=semester,
                                         number=1,
                                         hours="MW 1200-1400")
        section.students.add(stud)
        section.save()

    def test_section_view_exists(self):
        self.assertEqual(self.simple('/professor/sections/1/section'), 200)

    def test_section_grade_posts(self):
        stud = Student.objects.get(pk=1)
        login = self.client.login(username='u1', password='hello')
        response = self.client.post('/professor/sections/1/section',
                                    data={
                                        'sectionid': 1,
                                        'student': stud
                                    })
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/professor/sections/1/section',
                                    data={
                                        'sectionid': 1,
                                        'student': stud,
                                        str(stud): 3
                                    })
        self.assertEqual(response.status_code, 200)


class ProfessorAddReferenceViewTest(TestCase):

    @classmethod
    def setUpTestData(self):
        ad = createAdmin('foobar').profile
        major = Major.objects.create(abbreviation="CPSC", title="Computer Science", contact=ad)
        prof = createProfessor(username='u1', password='hello', major=major)
        stud = createStudent(username='u2', password='hello', major=major)
        course = createCourse(major=major, num='101')
        semester = createSemester()
        section = Section.objects.create(course=course,
                                         professor=prof,
                                         semester=semester,
                                         number=1,
                                         hours="MW 1200-1400")
        section.students.add(stud)
        section.save()

    def test_add_reference_view_exists(self):
        self.client.login(username='u1', password='hello')
        self.assertEqual(self.simple('/professor/course/1/add-reference'), 200)

    def test_add_reference_form_post(self):
        self.client.login(username='u1', password='hello')
        response = self.client.post('/professor/course/1/add-reference',
                                    data={
                                        'title': 'new thing',
                                        'description': 'describe it',
                                        'link': 'https://www.testingaddreference.io',
                                        'edition': '2nd',
                                        'type': 'ass',
                                    })
        self.assertEqual(response.status_code, 302)

    def test_add_reference_missing_info(self):
        self.client.login(username='u1', password='hello')
        response = self.client.get('/professor/course/1/add-reference',
                                   data={
                                       'description': 'describe it',
                                       'link': 'https://www.testingaddreference.io',
                                       'edition': '2nd',
                                   })
        self.assertEqual(response.status_code, 200)
