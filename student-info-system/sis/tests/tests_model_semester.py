from django.test import TestCase
from datetime import datetime, timedelta

from django.contrib.auth.models import User

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, Student, ClassLevel, Profile)

from sis.tests.utils import *


class Semester_tests(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(Semester_tests, cls).setUpTestData()
        Semester_tests.s1 = createSemester(offsets=(0, 1, 1, 1, 2, 3))

    def test_names(self):
        self.assertEqual(Semester.name_for_session(Semester.FALL), 'Fall')
        self.assertEqual(Semester.name_for_session(Semester.SPRING), 'Spring')
        self.assertEqual(Semester.name_for_session(Semester.SUMMER), 'Summer')
        self.assertEqual(Semester.name_for_session(Semester.WINTER), 'Winter')

    def test_bad_name(self):
        self.assertRaises(Exception, Semester.name_for_session('xx'))

    def test_order_fields(self):
        # forcing the fetch here lets the annotation generate the extra attributes
        s2 = Semester.objects.get(year=2020)

        self.assertEqual(s2.session_name, 'Fall')
        self.assertEqual(s2.session_order, 0)

    def test_reg_open(self):
        self.assertTrue(Semester_tests.s1.registration_open())

    def test_reg_open_not(self):
        self.assertFalse(
            Semester_tests.s1.registration_open(when=datetime.now() - timedelta(days=1)))
        self.assertFalse(
            Semester_tests.s1.registration_open(when=datetime.now() + timedelta(days=3)))

    def test_in_session(self):
        s1 = Semester_tests.s1
        self.assertTrue(Semester_tests.s1.in_session(when=datetime.now() + timedelta(days=1.5)))

    def test_in_session_not(self):
        self.assertFalse(Semester_tests.s1.in_session(when=datetime.now() - timedelta(days=1)))
        self.assertFalse(Semester_tests.s1.in_session(when=datetime.now() + timedelta(days=3)))

    def test_preparing_grades(self):
        self.assertTrue(
            Semester_tests.s1.preparing_grades(when=datetime.now() + timedelta(days=2)))

    def test_preparing_grades_not(self):
        self.assertFalse(
            Semester_tests.s1.preparing_grades(when=datetime.now() - timedelta(days=1)))
        self.assertFalse(
            Semester_tests.s1.preparing_grades(when=datetime.now() + timedelta(days=20)))

    def test_finalized(self):
        self.assertTrue(Semester_tests.s1.finalized(when=datetime.now() + timedelta(days=20)))

    def test_finalized_not(self):
        self.assertFalse(Semester_tests.s1.finalized(when=datetime.now() - timedelta(days=1)))
        self.assertFalse(Semester_tests.s1.finalized(when=datetime.now() + timedelta(days=1)))

    def test_drop_possible(self):
        s2 = createSemester(offsets=(0, 0, 0, 1, 1, 2), session=Semester.WINTER)
        self.assertTrue(s2.drop_possible())
        s2.delete()

    def test_drop_possible_not(self):
        s2 = createSemester(date_ended=1, date_last_drop=1, session=Semester.WINTER)
        self.assertFalse(s2.drop_possible(when=datetime.now() - timedelta(days=1)))
        self.assertFalse(s2.drop_possible(when=datetime.now() + timedelta(days=3)))
        s2.delete()

    def test_current_semester_is(self):
        s2 = createSemester(date_started=4, date_ended=7, session=Semester.WINTER)
        self.assertEqual(Semester.current_semester(at=datetime.now() + timedelta(days=4.5)), s2)
