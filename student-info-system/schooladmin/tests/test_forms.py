from django.test import TestCase

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, Student, ClassLevel)

from schooladmin.forms import (CourseEditForm, CourseCreationForm)

from sis.tests.utils import *


class CourseCreation_formtest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(CourseCreation_formtest, cls).setUpTestData()
        ad = createAdmin('foobar').profile
        CourseCreation_formtest.m = Major.objects.create(abbreviation='ABCD',
                                                         title='The A, The B',
                                                         contact=ad)
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
        self.assertEqual(c2.catalog_number, 102)
        self.assertEqual(c2.description, 'descr')
        self.assertEqual(c2.credits_earned, 3.0)

    def test_long_catnumber(self):
        form = CourseCreationForm({
            'major': CourseCreation_formtest.m.id,
            'title': 'the titlicious',
            'catalog_number': '-2',
            'description': 'descr',
            'credits_earned': '3.0',
            'prereqs': [],
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'catalog_number': ['Ensure this value is greater than or equal to 1.'],
        })


class CourseEdit_formtest(TestCase):

    @classmethod
    def setUpTestData(cls):
        KLASS = CourseEdit_formtest
        super(CourseEdit_formtest, cls).setUpTestData()
        ad = createAdmin('foobar').profile
        KLASS.m = Major.objects.create(abbreviation='ABCD', title='The A, The B', contact=ad)
        KLASS.m1 = Major.objects.create(abbreviation='ASDF', title='The A, The B', contact=ad)
        KLASS.c1 = createCourse(KLASS.m, 101)

    def test_valid_data(self):
        KLASS = self.__class__
        form = CourseEditForm(
            {
                'major': KLASS.m1.id,
                'title': 'the titlicious',
                'catalog_number': '102',
                'description': 'descr',
                'credits_earned': '3.0',
                'prereqs': [],
            },
            instance=KLASS.c1)
        self.assertEqual(form.errors, {})
        self.assertTrue(form.is_valid())
        c2 = form.save()
        self.assertEqual(c2.name, 'ASDF-102')
        self.assertEqual(c2.title, 'the titlicious')
        self.assertEqual(c2.catalog_number, 102)
        self.assertEqual(c2.description, 'descr')
        self.assertEqual(c2.credits_earned, 3.0)

    def test_null_catnumber(self):
        KLASS = self.__class__
        form = CourseEditForm(
            {
                'major': KLASS.m1.id,
                'title': 'the titlicious',
                'catalog_number': '',
                'description': 'descr',
                'credits_earned': '3.0',
                'prereqs': [],
            },
            instance=KLASS.c1)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'catalog_number': ['This field is required.'],
        })

    def test_long_catnumber(self):
        KLASS = self.__class__
        form = CourseEditForm(
            {
                'major': KLASS.m1.id,
                'title': 'the titlicious',
                'catalog_number': '-1',
                'description': 'descr',
                'credits_earned': '3.0',
                'prereqs': [],
            },
            instance=KLASS.c1)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'catalog_number': ['Ensure this value is greater than or equal to 1.'],
        })
