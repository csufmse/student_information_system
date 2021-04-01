from django.test import TestCase
from datetime import datetime

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, Student, TranscriptRequest, AccessRoles, ClassLevel)

from sis.tests.utils import (createStudent, createProfessor, createAdmin, createCourse)


class CourseTestCase_Basic(TestCase):

    def setUp(self):
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        Course.objects.create(major=major,
                              catalog_number='101',
                              title="Intro To Test",
                              credits_earned=3.0)

    def test_course_major_name(self):
        course = Course.objects.get(title="Intro To Test")
        self.assertEqual(course.major_name, "Computer Science")

    def test_course_name(self):
        course = Course.objects.get(title="Intro To Test")
        self.assertEqual(course.name, "CPSC-101")

    def test_course_descr(self):
        course = Course.objects.get(title="Intro To Test")
        self.assertEqual(course.descr, "CPSC-101: Intro To Test")

    def test_major(self):
        course = Course.objects.get(title="Intro To Test")
        self.assertEqual(course.major_name, "Computer Science")


class CourseTestCase_deps(TestCase):

    @classmethod
    def setUpTestData(cls):
        m = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        CourseTestCase_deps.major = m

        CourseTestCase_deps.courses = {}
        for i in range(1, 15):
            CourseTestCase_deps.courses[i] = createCourse(m, str(i))

    def test_none(self):
        cs = CourseTestCase_deps.courses
        self.assertEqual(cs[1].are_candidate_prerequisites_valid(), True)

    def test_valid_candidate(self):
        cs = CourseTestCase_deps.courses
        self.assertEqual(cs[1].are_candidate_prerequisites_valid([cs[2]]), True)

    def test_candidate_loop(self):
        cs = CourseTestCase_deps.courses
        self.assertEqual(cs[1].are_candidate_prerequisites_valid([cs[1]]), False)

    def test_candidate_chain(self):
        cs = CourseTestCase_deps.courses
        cp = CoursePrerequisite.objects.create(course=cs[2], prerequisite=cs[3])
        self.assertEqual(cs[1].are_candidate_prerequisites_valid([cs[2]]), True)
        cp.delete()

    def test_candidate_loop(self):
        cs = CourseTestCase_deps.courses
        cp1 = CoursePrerequisite.objects.create(course=cs[2], prerequisite=cs[3])
        cp2 = CoursePrerequisite.objects.create(course=cs[3], prerequisite=cs[1])
        self.assertEqual(cs[1].are_candidate_prerequisites_valid([cs[2]]), False)
        cp1.delete()
        cp2.delete()

    def test_double_dep(self):
        cs = CourseTestCase_deps.courses
        cp1 = CoursePrerequisite.objects.create(course=cs[2], prerequisite=cs[3])
        cp2 = CoursePrerequisite.objects.create(course=cs[5], prerequisite=cs[3])
        self.assertEqual(cs[1].are_candidate_prerequisites_valid([cs[2], cs[5]]), True)
        cp1.delete()
        cp2.delete()

    def test_offset(self):
        cs = CourseTestCase_deps.courses

        def cp(c, p):
            return CoursePrerequisite.objects.create(course=cs[c], prerequisite=cs[p])

        cp(1, 11)
        cp(11, 5)
        cp(1, 5)
        cp(5, 6)
        cp(6, 7)
        self.assertEqual(cs[1].are_candidate_prerequisites_valid(), True)


class CourseTestCase_edit(TestCase):

    @classmethod
    def setUpTestData(cls):
        m = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        CourseTestCase_edit.m1 = Major.objects.create(abbreviation='XYAZ', name='Bananas')
        CourseTestCase_edit.major = m

        CourseTestCase_edit.courses = {}
        for i in range(1, 15):
            CourseTestCase_edit.courses[i] = createCourse(m, str(i))

    def test_editnumber(self):
        c = CourseTestCase_edit.courses[1]
        self.assertEqual(c.catalog_number, '1')
        c.catalog_number = '923'
        c.save()
        c1 = Course.objects.get(id=1)
        self.assertEqual(c1.catalog_number, '923')

    def test_edittitle(self):
        c = CourseTestCase_edit.courses[1]
        self.assertEqual(c.title, 'c1')
        c.title = 'my new name'
        c.save()
        c1 = Course.objects.get(id=1)
        self.assertEqual(c1.title, 'my new name')

    def test_editdescr(self):
        c = CourseTestCase_edit.courses[1]
        self.assertEqual(c.description, 'course 1')
        c.description = 'amazing facts'
        c.save()
        c1 = Course.objects.get(id=1)
        self.assertEqual(c1.description, 'amazing facts')

    def test_editcredits(self):
        c = CourseTestCase_edit.courses[1]
        self.assertEqual(c.credits_earned, 1.0)
        c.credits_earned = 6.4
        c.save()
        c1 = Course.objects.get(id=1)
        self.assertEqual(float(c1.credits_earned), 6.4)

    def test_edit_major(self):
        c = CourseTestCase_edit.courses[1]
        self.assertEqual(c.major_name, 'Computer Science')
        c.major = CourseTestCase_edit.m1
        c.save()
        c1 = Course.objects.get(id=1)
        self.assertEqual(c1.major_name, 'Bananas')
