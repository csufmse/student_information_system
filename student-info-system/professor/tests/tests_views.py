from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Profile, Section,
                        SectionStudent, Semester, SemesterStudent, Student, UpperField)


class ProfessorSectionViewsTest(TestCase):

    @classmethod
    def setUpTestData(self):
        major = Major.objects.create(abbreviation="CPSC", title="Computer Science")
        u1 = User.objects.create_user(username='u1',
                                      first_name='p',
                                      last_name='rof',
                                      password='hello')
        u2 = User.objects.create_user(username='u2', first_name='s', password='hello')
        profile = Profile.objects.create(user=u1, role='P')
        sprofile = Profile.objects.create(user=u2, role='S')
        prof = Professor.objects.create(profile=profile, major=major)
        stud = Student.objects.create(profile=sprofile, major=major)
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_registration_closes=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           session=Semester.FALL,
                                           year=2000)
        section = Section.objects.create(course=course,
                                         professor=prof,
                                         semester=semester,
                                         number=1,
                                         hours="MW 1200-1400")

    # list views
    def test_sections_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/professor/sections')
        self.assertEqual(response.status_code, 200)

    def test_student_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/professor/section/students/1/student')
        self.assertEqual(response.status_code, 200)


class ProfessorStudentsInSectionViewsTest(TestCase):

    @classmethod
    def setUpTestData(self):
        major = Major.objects.create(abbreviation="CPSC", title="Computer Science")
        u1 = User.objects.create_user(username='u1',
                                      first_name='p',
                                      last_name='rof',
                                      password='hello')
        u2 = User.objects.create_user(username='u2',
                                      first_name='s',
                                      last_name='tud',
                                      password='hello')
        pprofile = Profile.objects.create(user=u1, role='P')
        sprofile = Profile.objects.create(user=u2, role='S')
        prof = Professor.objects.create(profile=pprofile, major=major)
        stud = Student.objects.create(profile=sprofile, major=major)
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_registration_closes=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           session=Semester.FALL,
                                           year=2000)
        section = Section.objects.create(course=course,
                                         professor=prof,
                                         semester=semester,
                                         number=1,
                                         hours="MW 1200-1400")
        section.students.add(stud)
        section.save()

    def test_studentsinsection_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/professor/section/1/students')
        self.assertEqual(response.status_code, 200)

    def test_studentsinsection_grade_posts(self):
        stud = Student.objects.get(pk=1)
        login = self.client.login(username='u1', password='hello')
        response = self.client.post('/professor/section/1/students',
                                    data={
                                        'sectionid': 1,
                                        'student': stud
                                    })
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/professor/section/1/students',
                                    data={
                                        'secctionid': 1,
                                        'student': stud,
                                        str(stud): 3
                                    })
        self.assertEqual(response.status_code, 200)
