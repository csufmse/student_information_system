from django.test import TestCase

from sis.models import (
    Course,
    Major,
)

from sis.tests.utils import *


class AdminMajorViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        KLASS = AdminMajorViewsTest
        super(KLASS, cls).setUpTestData()
        KLASS.test_user1 = createAdmin(username='u1', password='hello')
        KLASS.m1 = Major.objects.create(abbreviation="CPSC",
                                        title="Computer Science",
                                        contact=KLASS.test_user1.profile)
        KLASS.m2 = Major.objects.create(abbreviation="ENGL",
                                        title="English",
                                        contact=KLASS.test_user1.profile)
        KLASS.m3 = Major.objects.create(abbreviation="LIT",
                                        title="Literature",
                                        contact=KLASS.test_user1.profile)
        KLASS.c1 = Course.objects.create(major=KLASS.m1,
                                         catalog_number='101',
                                         title="Intro To Test",
                                         credits_earned=3.0)
        KLASS.c2 = Course.objects.create(major=KLASS.m1,
                                         catalog_number='102',
                                         title="More Test",
                                         credits_earned=3.0)
        KLASS.c3 = Course.objects.create(major=KLASS.m3,
                                         catalog_number='101',
                                         title="something else",
                                         credits_earned=3.0)
        KLASS.m1.courses_required.add(KLASS.c1)
        KLASS.m1.courses_required.add(KLASS.c3)
        KLASS.m1.save()

    def test_majors_view_exists(self):
        self.assertEqual(self.simple('/sis/majors'), 200)

    def test_majors_view_uses_template(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/sis/majors')
        self.assertTemplateUsed(response, 'sis/majors.html')

    # single-object views
    def test_major_view_exists(self):
        self.assertEqual(self.simple('/sis/major/' + str(AdminMajorViewsTest.m1.id)), 200)

    def test_nonexistent_major_fails_view(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/sis/major/' + '445455554')
        self.assertEqual(response.status_code, 404)

    def test_major_view_uses_template(self):
        login = self.client.login(username='u1', password='hello')
        response = self.client.get('/sis/major/' + str(AdminMajorViewsTest.m1.id))
        self.assertTemplateUsed(response, 'sis/major.html')
