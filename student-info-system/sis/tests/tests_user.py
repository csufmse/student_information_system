from django.test import TestCase

from sis.tests.utils import *


class CommonUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(CommonUserViews, cls).setUpTestData()
        CommonUserViews.u1 = createAdmin(username='u1', password='hello')

    # misc
    def test_user_pass_change_view_exists(self):
        self.assertEqual(self.simple('/sis/user/1/change_password'), 200)
