from django.test import TestCase
from sis.tests.utils import *


class ProfileUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ProfileUserViews, cls).setUpTestData()
        createAdmin(username='u1', password='hello')

    # list views
    def test_profile_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/profile'), 200)

    # Single-object views
    def test_profile_edit_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/profile/edit'), 200)
