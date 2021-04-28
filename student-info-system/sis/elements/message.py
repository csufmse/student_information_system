from django import forms
from django.db.models import Value
from django.db.models.functions import Concat
import django_tables2 as tables
from django_filters import (CharFilter, ChoiceFilter, DateTimeFromToRangeFilter, FilterSet)

from sis.elements.utils import *

from sis.models import (Message, Profile)


class FullSentMessageFilter(FilterSet):
    prefix = 'sent'
    BOOLE_CHOICES = ((True, 'Only Archived'), (False, 'Only Not Archived'))
    HANDLED_CHOICES = ((True, 'Only Handled'), (False, 'Only Unhandled'))

    time_sent = DateTimeFromToRangeFilter()
    sender = CharFilter(field_name='sender__user__name',
                        label='From',
                        method='filter_sender',
                        lookup_expr='icontains')
    recipient = CharFilter(field_name='recipient__user__name',
                           label='To',
                           method='filter_recipient',
                           lookup_expr='icontains')
    unread = ChoiceFilter(field_name='unread',
                          label='Read?',
                          choices=((True, 'Unread Only'), (False, 'Read Only')))
    archived = ChoiceFilter(field_name='archived',
                            label='Archived?',
                            choices=BOOLE_CHOICES,
                            initial=False)
    handled = ChoiceFilter(field_name='handled', label='Handled?', choices=HANDLED_CHOICES)
    subject = CharFilter(field_name='subject', lookup_expr='icontains')
    high_priority = ChoiceFilter(label='High Pri?',
                                 choices=((True, 'High Pri'), (False, 'Normal')))
    body = CharFilter(field_name='body', lookup_expr='icontains')

    def filter_recipient(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'recipient__user__username',
            Value('-'),
            'recipient__user__first_name',
            Value(' '),
            'recipient__user__last_name',
        )).filter(slug__icontains=value)

    def filter_sender(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'sender__user__username',
            Value('-'),
            'sender__user__first_name',
            Value(' '),
            'sender__user__last_name',
        )).filter(slug__icontains=value)

    def __init__(self, data=None, *args, **kwargs):
        newdict = data.dict()
        if len(newdict) == 0:
            newdict[f'{self.prefix}-archived'] = False
        super(FullSentMessageFilter, self).__init__(newdict, *args, **kwargs)
        self.filters['high_priority'].extra.update({'empty_label': 'Any Pri'})
        self.filters['unread'].extra.update({'empty_label': 'Read/Unread'})
        self.filters['archived'].extra.update({'empty_label': 'Archived?'})
        self.filters['handled'].extra.update({'empty_label': 'Handled?'})

    class Meta:
        fields = [
            'time_sent',
            'sender',
            'recipient',
            'subject',
            'unread',
            'high_priority',
            'archived',
            'handled',
        ]


class FullReceivedMessageFilter(FilterSet):
    prefix = 'received'

    BOOLE_CHOICES = ((True, 'Only Archived'), (False, 'Only Not Archived'))
    HANDLED_CHOICES = ((True, 'Only Handled'), (False, 'Only Unhandled'))

    time_sent = DateTimeFromToRangeFilter()
    sender = CharFilter(field_name='sender__user__name',
                        label='Frxom',
                        method='filter_sender',
                        lookup_expr='icontains')
    unread = ChoiceFilter(field_name='unread',
                          label='Read?',
                          choices=((True, 'Unread Only'), (False, 'Read Only')))
    archived = ChoiceFilter(field_name='archived',
                            label='Archived?',
                            choices=BOOLE_CHOICES,
                            initial=False)
    subject = CharFilter(field_name='subject', lookup_expr='icontains')
    handled = ChoiceFilter(field_name='handled', label='Handled?', choices=HANDLED_CHOICES)
    high_priority = ChoiceFilter(label='High Pri?',
                                 choices=((True, 'High Pri'), (False, 'Normal')))

    def filter_recipient(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'recipient__user__username',
            Value('-'),
            'recipient__user__first_name',
            Value(' '),
            'recipient__user__last_name',
        )).filter(slug__icontains=value)

    def filter_sender(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'sender__user__username',
            Value('-'),
            'sender__user__first_name',
            Value(' '),
            'sender__user__last_name',
        )).filter(slug__icontains=value)

    def __init__(self, data=None, *args, **kwargs):
        newdict = data.dict()
        if len(newdict) == 0:
            newdict[f'{self.prefix}-archived'] = False
        super(FullReceivedMessageFilter, self).__init__(newdict, *args, **kwargs)

        self.filters['high_priority'].extra.update({'empty_label': 'Any Pri'})
        self.filters['unread'].extra.update({'empty_label': 'Read/Unread'})
        self.filters['archived'].extra.update({'empty_label': 'Archived?'})
        self.filters['handled'].extra.update({'empty_label': 'Handled?'})

    class Meta:
        fields = [
            'time_sent', 'sender', 'subject', 'unread', 'high_priority', 'handled', 'archived'
        ]


# no handled, no sender, no body filter
class SentMessageFilter(FilterSet):
    prefix = 'sent'

    BOOLE_CHOICES = ((True, 'Only Archived'), (False, 'Only Not Archived'))

    time_sent = DateTimeFromToRangeFilter()
    recipient = CharFilter(field_name='recipient__user__name',
                           label='To',
                           method='filter_recipient',
                           lookup_expr='icontains')
    unread = ChoiceFilter(field_name='unread',
                          label='Read?',
                          choices=((True, 'Unread Only'), (False, 'Read Only')))
    subject = CharFilter(field_name='subject', lookup_expr='icontains')
    high_priority = ChoiceFilter(label='High Pri?',
                                 choices=((True, 'High Pri'), (False, 'Normal')))

    def filter_recipient(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'recipient__user__username',
            Value('-'),
            'recipient__user__first_name',
            Value(' '),
            'recipient__user__last_name',
        )).filter(slug__icontains=value)

    def __init__(self, data=None, *args, **kwargs):
        newdict = data.dict()
        if len(newdict) == 0:
            newdict[f'{self.prefix}-archived'] = False
        super(SentMessageFilter, self).__init__(newdict, *args, **kwargs)
        self.filters['high_priority'].extra.update({'empty_label': 'Any Pri'})
        self.filters['unread'].extra.update({'empty_label': 'Read/Unread'})

    class Meta:
        fields = ['time_sent', 'recipient', 'subject', 'unread', 'high_priority']


# no recipient, no handled, no body filter
class ReceivedMessageFilter(FilterSet):
    prefix = 'received'

    BOOLE_CHOICES = ((True, 'Only Archived'), (False, 'Only Not Archived'))
    HANDLED_CHOICES = ((True, 'Only Handled'), (False, 'Only Unhandled'))

    time_sent = DateTimeFromToRangeFilter()
    sender = CharFilter(field_name='sender__user__name',
                        label='From',
                        method='filter_sender',
                        lookup_expr='icontains')
    unread = ChoiceFilter(field_name='unread',
                          label='Read?',
                          choices=((True, 'Unread Only'), (False, 'Read Only')))
    archived = ChoiceFilter(field_name='archived', label='Archived?', choices=BOOLE_CHOICES)
    subject = CharFilter(field_name='subject', lookup_expr='icontains')
    high_priority = ChoiceFilter(label='High Pri?',
                                 choices=((True, 'High Pri'), (False, 'Normal')))

    def filter_sender(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'sender__user__username',
            Value('-'),
            'sender__user__first_name',
            Value(' '),
            'sender__user__last_name',
        )).filter(slug__icontains=value)

    def __init__(self, data=None, *args, **kwargs):
        newdict = data.dict()
        if len(newdict) == 0:
            newdict[f'{self.prefix}-archived'] = False
        super(ReceivedMessageFilter, self).__init__(newdict, *args, **kwargs)
        self.form.initial['archived'] = 'Only Not Archived'
        self.filters['high_priority'].extra.update({'empty_label': 'Any Pri'})
        self.filters['unread'].extra.update({'empty_label': 'Read/Unread'})
        self.filters['archived'].extra.update({'empty_label': 'Archived?'})

    class Meta:
        fields = ['time_sent', 'sender', 'subject', 'unread', 'archived', 'high_priority']


class MessageDetailForm(forms.ModelForm):
    role = forms.ChoiceField(choices=Profile.ROLES,
                             required=True,
                             help_text='Select type of user')
    role.widget.attrs.update({'class': 'role_sel selectpicker'})

    bio = forms.CharField(max_length=256,
                          required=False,
                          widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Profile
        fields = ('role', 'bio')


def classes_for(record=None, row_class="message_row"):
    cl = row_class
    if record is not None:
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
            'class': (lambda record: classes_for(record)),
            'data-id': lambda record: record.pk
        }
        attrs = {"class": 'message_table'}


class MessageReceivedTable(MessageTable):

    class Meta:
        exclude = ('recipient', 'time_read')
        row_attrs = {
            'class': (lambda record: classes_for(record, 'received-row')),
            'data-id': lambda record: record.pk
        }
        attrs = {"class": 'message_table'}


class StudentMessageReceivedTable(MessageReceivedTable):

    class Meta:
        exclude = ('handled',)
        row_attrs = {
            'class': (lambda record: classes_for(record, 'received-row')),
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
            'class': (lambda record: classes_for(record, 'sent-row')),
            'data-id': lambda record: record.pk
        }
        attrs = {"class": 'message_table'}
