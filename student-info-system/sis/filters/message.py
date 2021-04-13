import django_filters
from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Concat
from django_filters import (CharFilter, ChoiceFilter, DateTimeFromToRangeFilter, FilterSet,
                            ModelChoiceFilter, BooleanFilter, RangeFilter)

from sis.models import (Message, Profile)


class FullMessageFilter(FilterSet):
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
    archived = ChoiceFilter(field_name='archived', label='Archived?', choices=BOOLE_CHOICES)
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

    def __init__(self, *args, **kwargs):
        super(FullMessageFilter, self).__init__(*args, **kwargs)
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


class FullSentMessageFilter(FullMessageFilter):
    prefix = 'sent'

    class Meta:
        fields = ['time_sent', 'recipient', 'subject', 'unread', 'high_priority', 'archived']


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

    def __init__(self, *args, **kwargs):
        super(SentMessageFilter, self).__init__(*args, **kwargs)
        self.filters['high_priority'].extra.update({'empty_label': 'Any Pri'})
        self.filters['unread'].extra.update({'empty_label': 'Read/Unread'})

    class Meta:
        fields = ['time_sent', 'recipient', 'subject', 'unread', 'high_priority']


class FullReceivedMessageFilter(FullMessageFilter):
    prefix = 'received'

    class Meta:
        fields = ['time_sent', 'sender', 'subject', 'unread', 'high_priority', 'archived']


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

    def __init__(self, *args, **kwargs):
        super(ReceivedMessageFilter, self).__init__(*args, **kwargs)
        self.filters['high_priority'].extra.update({'empty_label': 'Any Pri'})
        self.filters['unread'].extra.update({'empty_label': 'Read/Unread'})
        self.filters['archived'].extra.update({'empty_label': 'Archived?'})

    class Meta:
        fields = ['time_sent', 'sender', 'subject', 'unread', 'archived', 'high_priority']
