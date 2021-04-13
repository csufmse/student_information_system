from django.test import TestCase
from sis.tests.utils import *


class StudentUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(StudentUserViews, cls).setUpTestData()
        createAdmin(username='u1', password='hello')
        StudentUserViews.stud = createStudent(username='s1')

    # list views
    def test_students_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/students'), 200)

    # Single-object views
    def test_student_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/student/1'), 200)

    def test_student_transcript_exists(self):
        student_id = StudentUserViews.stud.profile.user.id
        self.assertEqual(self.simple(f'/schooladmin/student/{student_id}/transcript'), 200)
