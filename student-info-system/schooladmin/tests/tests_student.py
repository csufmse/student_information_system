from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Student, Course, CoursePrerequisite, Major, Professor, Section,
                        SectionStudent, Semester, SemesterStudent, Student, UpperField)

from sis.tests.utils import (createStudent, createProfessor, createAdmin, createCourse)


class StudentUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(StudentUserViews, cls).setUpTestData()
        StudentUserViews.u1 = createAdmin(username='frodo')

    # list views
    def test_students_view_exists(self):
        login = self.client.login(username='frodo', password='frodo1')
        response = self.client.get('/schooladmin/students')
        self.assertEqual(response.status_code, 200)

    # single-object views
    # WAITING FOR MERGE -- BJM
    # def test_student_view_exists(self):
    #     login = self.client.login(username='frodo', password='frodo1')
    #     response = self.client.get('/schooladmin/student/1')
    #     self.assertEqual(response.status_code, 200)
