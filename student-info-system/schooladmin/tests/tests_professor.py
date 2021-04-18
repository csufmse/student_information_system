from django.test import TestCase
from sis.tests.utils import *


class ProfessorUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ProfessorUserViews, cls).setUpTestData()
        ad = createAdmin(username='u1', password='hello')
        major = Major.objects.create(abbreviation="CPSC",
                                     title="Computer Science", contact=ad.profile)
        ProfessorUserViews.prof = createProfessor(username='p1',
                                                  major=major).profile.user.id

    # list views
    def test_prof_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/professors'), 200)

    # Single-object views
    def test_prof_view_exists(self):
        self.assertEqual(self.simple(f'/schooladmin/professor/' +
                                     f'{ProfessorUserViews.prof}'), 200)

    def test_prof_items_exists(self):
        self.assertEqual(self.simple(f'/schooladmin/professor/' +
                                     f'{ProfessorUserViews.prof}/items'), 200)

    def test_prof_item_new_exists(self):
        self.assertEqual(self.simple(f'/schooladmin/professor/' +
                                     f'{ProfessorUserViews.prof}/item_new'), 200)

    def test_prof_item_detail_exists(self):
        self.assertEqual(self.simple(f'/schooladmin/professor/' +
                                     f'{ProfessorUserViews.prof}/item/1'), 200)
