from django.test import TestCase

from sis.tests.utils import *


class SriViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(CommonUserViews, cls).setUpTestData()
        CommonUserViews.u1 = createAdmin(username='u1', password='hello')

    # misc
    def test_sec_item_view_exists(self):
        self.assertEqual(self.simple('/sis/secitem/1'), 200)
