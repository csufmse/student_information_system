from django.test import TestCase
from sis.tests.utils import *
from sis.models import Message


class MessageViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(MessageViews, cls).setUpTestData()
        u = createAdmin(username='u1', password='hello')
        Message.objects.create(sender=u.profile, recipient=u.profile, subject='foo')

    # list views
    def test_messages_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/messages'), 200)

    # Single-object views
    def test_student_view_exists(self):
        self.assertEqual(self.simple('/schooladmin/message/1'), 200)
