from django.test import TestCase

from sis.tests.utils import *


class AdminUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(AdminUserViews, cls).setUpTestData()
        AdminUserViews.u1 = createAdmin(username='u1', password='hello')

    # list views
    def test_users_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/users'), 200)

    # single-object views
    def test_user_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/user/1'), 200)

    # edit views
    def test_edit_user_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/user/1/edit'), 200)

    # create views
    def test_new_user_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/user_new'), 200)

    # misc
    def test_user_pass_change_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/user/1/change_password'), 200)
