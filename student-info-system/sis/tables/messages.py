import django_tables2 as tables

from sis.models import Message
from sis.tables import *

def classes_for(record):
    cl = 'message_row'
    if record.unread:
        cl += ' unread'
    if record.time_archived is not None:
        cl += ' archived'

    return cl

class MessageTable(tables.Table):
    recipient = ClassyColumn(verbose_name="To", css_class_base='message_addr')
    sender = ClassyColumn(verbose_name="From", css_class_base='message_addr')
    time_read = ClassyDateTimeColumn(verbose_name="Read at",
                                     css_class_base='message_date',
                                     format='Y-m-d H:i')
    time_sent = ClassyDateTimeColumn(verbose_name="Sent at",
                                     css_class_base='message_date',
                                     format='Y-m-d H:i')
    subject = ClassyColumn(verbose_name="Subject", css_class_base='message_subject')
    high_priority = ClassyColumn(verbose_name="Priority", css_class_base='message_priority')

    def render_high_priority(self, value):
        if value is not None and value:
            show = "*"
        else:
            show = ""
        return show

    unread = ClassyColumn(verbose_name="New", accessor='unread', css_class_base='message_unread')

    def render_unread(self, value, record):
        if value:
            show = "*"
        else:
            show = ""
        return show

    class Meta:
        model = Message
        template_name = "django_tables2/bootstrap.html"
        fields = ('unread', 'high_priority', 'time_sent', 'recipient', 'sender', 'subject')
        row_attrs = {
            'class': (lambda record: 'message_row unread' if record.unread else 'message_row'),
            'data-id': lambda record: record.pk
        }
        attrs = {"class": 'message_table'}

class MessageReceivedTable(MessageTable):

    class Meta:
        exclude = ('recipient', 'time_read')
        row_attrs = {
            'class': (lambda record: classes_for(record)),
            'data-id': lambda record: record.pk
        }
        attrs = {"class": 'message_table'}


class MessageSentTable(MessageTable):

    class Meta:
        exclude = ('sender', 'time_read')
        row_attrs = {
            'class': (lambda record: classes_for(record)),
            'data-id': lambda record: record.pk
        }
        attrs = {"class": 'message_table'}
