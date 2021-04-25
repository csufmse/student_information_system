from django.contrib.auth.models import User
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django_filters import (CharFilter, ChoiceFilter, FilterSet, ModelChoiceFilter)

from sis.models import (
    Major,
    Message,
    Professor,
    Semester,
    Student,
    Profile,
)


class UserFilter(FilterSet):
    username = CharFilter(lookup_expr='icontains')
    name = CharFilter(field_name='name',
                      label='Name',
                      method='filter_has_name',
                      lookup_expr='icontains')
    access_role = ChoiceFilter(field_name='profile__role',
                               label='Access Role',
                               choices=Profile.ROLES)
    major = ModelChoiceFilter(
        queryset=Major.objects.order_by('abbreviation'),
        # provided because it needs one. Will be ignoring this.
        field_name='name',
        method='filter_has_major',
        label='Major')

    def filter_has_major(self, queryset, name, value):
        return queryset.filter(
            Q(profile__professor__major__abbreviation=value) |
            Q(profile__student__major__abbreviation=value))

    def filter_has_name(self, queryset, name, value):
        return queryset.annotate(fullname=Concat('first_name', Value(' '), 'last_name')).filter(
            fullname__icontains=value).distinct()

    is_active = ChoiceFilter(label='Enabled?', choices=((True, 'Enabled'), (False, 'Disabled')))

    graduate = ChoiceFilter(field_name='profile__student__grad_student',
                            label='Grad Student?',
                            choices=((True, 'Grad Student'), (False, 'Undergrad')))

    class Meta:
        model = User
        fields = ['username', 'name', 'major', 'access_role', 'graduate', 'is_active']

    def __init__(self, *args, **kwargs):
        super(UserFilter, self).__init__(*args, **kwargs)
        self.filters['is_active'].extra.update({'empty_label': 'Enabled/Disabled'})
        self.filters['access_role'].extra.update({'empty_label': 'Any Role'})
        self.filters['major'].extra.update({'empty_label': 'Any Major/Dept'})
        self.filters['graduate'].extra.update({'empty_label': 'Grad/Undergrad'})


class StudentFilter(FilterSet):
    username = CharFilter(lookup_expr='icontains')
    name = CharFilter(field_name='name',
                      label='Name',
                      method='filter_has_name',
                      lookup_expr='icontains')
    major = ModelChoiceFilter(
        queryset=Major.objects.order_by('abbreviation'),
        # provided because it needs one. Will be ignoring this.
        field_name='name',
        method='filter_has_major',
        label='Major')

    def filter_has_major(self, queryset, name, value):
        return queryset.filter(profile__student__major__abbreviation=value)

    def filter_has_name(self, queryset, name, value):
        return queryset.annotate(fullname=Concat('first_name', Value(' '), 'last_name')).filter(
            fullname__icontains=value).distinct()

    is_active = ChoiceFilter(label='Enabled?', choices=((True, 'Enabled'), (False, 'Disabled')))

    graduate = ChoiceFilter(field_name='profile__student__grad_student',
                            label='Grad Student?',
                            choices=((True, 'Grad Student'), (False, 'Undergrad')))

    class Meta:
        model = User
        fields = ['username', 'name', 'major', 'graduate', 'is_active']

    def __init__(self, *args, **kwargs):
        super(StudentFilter, self).__init__(*args, **kwargs)
        self.filters['is_active'].extra.update({'empty_label': 'Enabled/Disabled'})
        self.filters['major'].extra.update({'empty_label': 'Any Major/Dept'})
        self.filters['graduate'].extra.update({'empty_label': 'Grad/Undergrad'})


class ProfessorFilter(FilterSet):
    username = CharFilter(lookup_expr='icontains')
    name = CharFilter(field_name='name',
                      label='Name',
                      method='filter_has_name',
                      lookup_expr='icontains')
    major = ModelChoiceFilter(
        queryset=Major.objects.order_by('abbreviation'),
        # provided because it needs one. Will be ignoring this.
        field_name='name',
        method='filter_has_major',
        label='Major')

    def filter_has_major(self, queryset, name, value):
        return queryset.filter(profile__professor__major__abbreviation=value)

    def filter_has_name(self, queryset, name, value):
        return queryset.annotate(fullname=Concat('first_name', Value(' '), 'last_name')).filter(
            fullname__icontains=value).distinct()

    class Meta:
        model = User
        fields = [
            'username',
            'name',
            'major',
        ]

    def __init__(self, *args, **kwargs):
        super(ProfessorFilter, self).__init__(*args, **kwargs)
        self.filters['major'].extra.update({'empty_label': 'Any Major/Dept'})
