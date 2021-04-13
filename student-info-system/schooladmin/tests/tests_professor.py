from django.test import TestCase
from sis.tests.utils import *


class ProfessorUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ProfessorUserViews, cls).setUpTestData()
        createAdmin(username='u1', password='hello')

    # list views
    # doesn't exist yet
    # def test_prof_view_exists(self):
    #     self.assertEqual(self.simple('/schooladmin/students'), 200)

    # Single-object views
    def test_prof_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/professor/1'), 200)

    def test_prof_items_exists(self):
        self.assertEqual(self.simple('/schooladmin/professor/1/items'), 200)

    def test_prof_item_new_exists(self):
        self.assertEqual(self.simple('/schooladmin/professor/1/item_new'), 200)

    def test_prof_item_detail_exists(self):
        self.assertEqual(self.simple('/schooladmin/professor/1/item/1'), 200)
