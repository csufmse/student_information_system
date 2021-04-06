from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, SemesterStudent, Student, UpperField)

from sis.tests.utils import (createStudent, createProfessor, createAdmin, createCourse)


class ProfessorSectionViewsTest(TestCase):

    @classmethod
    def setUpTestData(self):
        major = Major.objects.create(abbreviation="CPSC", title="Computer Science")
        prof = createProfessor(username='u1', password='hello', major=major)

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
        section = Section.objects.create(course=course,
                                         professor=prof,
                                         semester=semester,
                                         number=1,
                                         location="somewhere",
                                         hours="MW 1200-1400")

    # list views
    def test_sections_view_exists(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/professor/sections')
        self.assertEqual(response.status_code, 200)
