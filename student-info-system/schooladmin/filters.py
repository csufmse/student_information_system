from django.db.models import Q, F
from django_filters import (FilterSet, CharFilter, ChoiceFilter, ModelChoiceFilter,
                            ModelMultipleChoiceFilter)
from django.contrib.auth.models import User
from sis.models import Student, Admin, Professor, Major, Course


class UserFilter(FilterSet):
    username = CharFilter(lookup_expr='icontains')
    name = CharFilter(field_name='name', label='Name', lookup_expr='icontains')
    access_role = ChoiceFilter(field_name='access_role',
                               label='Access Role',
                               choices=(('Admin', 'Admin'), ('Professor', 'Professor'),
                                        ('Student', 'Student')))
    major = ModelChoiceFilter(queryset=Major.objects,
                                  # provided because it needs one. Will be ignoring this.
                                  field_name='name',
                                  method='filter_has_major',
                                  label='Major')

    def filter_has_major(self, queryset, name, value):
        return queryset.filter( Q(professor__major__abbreviation=value) | Q(student__major__abbreviation=value))

    is_active = ChoiceFilter(label='Enabled?', choices=((True, 'Enabled'), (False, 'Disabled')))

    class Meta:
        model = User
        fields = ['username', 'name', 'access_role', 'is_active']

    def __init__(self, *args, **kwargs):
        super(UserFilter, self).__init__(*args, **kwargs)
        self.filters['is_active'].extra.update(
            {'empty_label': 'Enabled/Disabled'})
        self.filters['access_role'].extra.update(
            {'empty_label': 'Any Role'})
        self.filters['major'].extra.update(
            {'empty_label': 'Any Major/Dept'})



class MajorFilter(FilterSet):
    abbreviation = CharFilter(field_name='abbreviation', lookup_expr='icontains')
    name = CharFilter(field_name='name', label='Name contains', lookup_expr='icontains')
    description = CharFilter(field_name='description',
                             label='Description contains',
                             lookup_expr='icontains')
#    professors = CharFilter(field_name='professor__user__last_name',
#                            lookup_expr='icontains',
#                            label='Has Professor')

    # requires = ModelChoiceFilter(field_name='requires',lookup_field='required_by',)

    professors = ModelChoiceFilter(queryset=Professor.objects,
                                  # provided because it needs one. Will be ignoring this.
                                  field_name='last_name',
                                  method='filter_has_prof',
                                  label='Professor')

    def filter_has_prof(self, queryset, name, value):
        return queryset.annotate(pname=F('professor__user__first_name') + ' ' + F('professor__user__last_name')).filter( pname__icontains=value )

    class Meta:
        model = Major
        fields = [
            'abbreviation',
            'name',
            'description',
            'professors',
            # 'requires'
        ]
