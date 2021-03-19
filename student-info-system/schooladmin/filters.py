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
    #    is_active = BooleanFilter(field_name='is_active',label="User Enabled")
    is_active = ChoiceFilter(label='Enabled?', choices=((True, 'Enabled'), (False, 'Disabled')))

    class Meta:
        model = User
        fields = ['username', 'name', 'access_role', 'is_active']


class MajorFilter(FilterSet):
    abbreviation = CharFilter(field_name='abbreviation', lookup_expr='icontains')
    name = CharFilter(field_name='name', label='Name contains', lookup_expr='icontains')
    description = CharFilter(field_name='description',
                             label='Description contains',
                             lookup_expr='icontains')
    # professors = ModelChoiceFilter(queryset=Professor.objects.filter(),
    #                               field_name='professor__user__last_name',
    #                               lookup_expr='icontains',label='Has Professor')
    professors = CharFilter(field_name='professor__user__last_name',
                            lookup_expr='icontains',
                            label='Has Professor')

    # requires = ModelChoiceFilter(field_name='requires',lookup_field='required_by',)

    class Meta:
        model = Major
        fields = [
            'abbreviation',
            'name',
            'description',
            'professors',
            # 'requires'
        ]
