from django.test import TestCase

from sis.models import Major
from sis.tests.utils import createAdmin, createStudent


class AdminTranscriptViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(AdminTranscriptViewTest, cls).setUpTestData()
        m = Major.objects.create(abbreviation='CPSC', title='CompSci')
        createAdmin(username='a', password='hello')
        AdminTranscriptViewTest.student = createStudent(username='s', password='hello', major=m)

    def test_transcript_view_exists(self):
        login = self.client.login(username='a', password='hello')
        response = self.client.get('/schooladmin/student/' +
                                   str(AdminTranscriptViewTest.student.profile.user.id) +
                                   '/transcript')
        self.assertEqual(response.status_code, 200)

    def test_transcript_uses_template(self):
        login = self.client.login(username='a', password='hello')
        response = self.client.get('/schooladmin/student/' +
                                   str(AdminTranscriptViewTest.student.profile.user.id) +
                                   '/transcript')
        self.assertTemplateUsed(response, 'schooladmin/transcript.html')
