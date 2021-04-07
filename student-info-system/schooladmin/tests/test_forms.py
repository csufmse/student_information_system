from django.test import TestCase
from datetime import datetime

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, Student, ClassLevel)

from schooladmin.forms import (CourseEditForm, CourseCreationForm)

from sis.tests.utils import (createStudent, createProfessor, createAdmin, createCourse)


class CourseCreation_formtest(TestCase):

    @classmethod
    def setUpTestData(self):
        CourseCreation_formtest.m = Major.objects.create(abbreviation='ABCD',
                                                         title='The A, The B')
        CourseCreation_formtest.c1 = createCourse(CourseCreation_formtest.m, 101)

    def test_blank_data(self):
        form = CourseCreationForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors, {
                'major': ['This field is required.'],
                'title': ['This field is required.'],
                'catalog_number': ['This field is required.'],
                'credits_earned': ['This field is required.'],
            })

    def test_valid_data(self):
        form = CourseCreationForm({
            'major': CourseCreation_formtest.m.id,
            'title': 'the titlicious',
            'catalog_number': '102',
            'description': 'descr',
            'credits_earned': '3.0',
            'prereqs': [],
        })
        self.assertTrue(form.is_valid())
        c2 = form.save()
        self.assertEqual(c2.name, 'ABCD-102')
        self.assertEqual(c2.title, 'the titlicious')
        self.assertEqual(c2.catalog_number, '102')
        self.assertEqual(c2.description, 'descr')
        self.assertEqual(c2.credits_earned, 3.0)

    def test_long_catnumber(self):
        form = CourseCreationForm({
            'major': CourseCreation_formtest.m.id,
            'title': 'the titlicious',
            'catalog_number': '999999999999999999999999999999',
            'description': 'descr',
            'credits_earned': '3.0',
            'prereqs': [],
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'catalog_number': ['Ensure this value has at most 20 characters (it has 30).'],
        })


class CourseEdit_formtest(TestCase):

    @classmethod
    def setUpTestData(self):
        CourseEdit_formtest.m = Major.objects.create(abbreviation='ABCD', title='The A, The B')
        CourseEdit_formtest.m1 = Major.objects.create(abbreviation='ASDF', title='The A, The B')
        CourseEdit_formtest.c1 = createCourse(CourseEdit_formtest.m, 101)

    def test_valid_data(self):
        form = CourseEditForm(
            {
                'major': CourseEdit_formtest.m1.id,
                'title': 'the titlicious',
                'catalog_number': '102',
                'description': 'descr',
                'credits_earned': '3.0',
                'prereqs': [],
            },
            instance=CourseEdit_formtest.c1)
        self.assertEqual(form.errors, {})
        self.assertTrue(form.is_valid())
        c2 = form.save()
        self.assertEqual(c2.name, 'ASDF-102')
        self.assertEqual(c2.title, 'the titlicious')
        self.assertEqual(c2.catalog_number, '102')
        self.assertEqual(c2.description, 'descr')
        self.assertEqual(c2.credits_earned, 3.0)

    def test_null_catnumber(self):
        form = CourseEditForm(
            {
                'major': CourseEdit_formtest.m1.id,
                'title': 'the titlicious',
                'catalog_number': '',
                'description': 'descr',
                'credits_earned': '3.0',
                'prereqs': [],
            },
            instance=CourseEdit_formtest.c1)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'catalog_number': ['This field is required.'],
        })

    def test_long_catnumber(self):
        form = CourseEditForm(
            {
                'major': CourseEdit_formtest.m1.id,
                'title': 'the titlicious',
                'catalog_number': '123451234512345123451234512345',
                'description': 'descr',
                'credits_earned': '3.0',
                'prereqs': [],
            },
            instance=CourseEdit_formtest.c1)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'catalog_number': ['Ensure this value has at most 20 characters (it has 30).'],
        })
