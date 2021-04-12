import django_tables2 as tables
from sis.models import Message
from sis.tables import *


def classes_for(record):
    cl = 'message_row'
    if record.unread:
        cl += ' unread'
    if record.time_archived is not None:
        cl += ' archived'
    if record.aged_request():
        cl += ' aged-request'

    return cl


class MessageTable(tables.Table):
    recipient = ClassyColumn(
        verbose_name="To",
        css_class_base='message_addr',
        order_by=("recipient__user__last_name", "recipient__user__first_name"),
    )
    sender = ClassyColumn(verbose_name="From",
                          css_class_base='message_addr',
                          order_by=("sender__user__last_name", "sender__user__first_name"))
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

    handled = ClassyColumn(verbose_name="Handled?",
                           accessor='time_handled',
                           css_class_base='message_handled')

    def render_handled(self, value, record):
        if value is not None:
            show = "Yes"
        else:
            show = "No"
        return show

    class Meta:
        model = Message
        template_name = "django_tables2/bootstrap.html"
        fields = ('unread', 'high_priority', 'time_sent', 'recipient', 'sender', 'subject',
                  'handled')
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
        exclude = (
            'sender',
            'time_read',
            'handled',
        )
        row_attrs = {
            'class': (lambda record: classes_for(record)),
            'data-id': lambda record: record.pk
        }
        attrs = {"class": 'message_table'}
