from django.db.models import Q, Value, F
from django.db.models.functions import Concat
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
# this version lets them type part of the profs name
    professors = CharFilter(field_name='professor__user__last_name',
                            lookup_expr='icontains',
                            label='Professor Name')
# this version lets them pick professors
#    professors = ModelChoiceFilter(queryset=Professor.objects,
#                                  method='filter_has_prof',
#                                  label='Has Professor')
#    def filter_has_prof(self, queryset, name, value):
#        return queryset.annotate(profname=Concat('professor__user__first_name',Value(' '),
#                                                 'professor__user__last_name')).filter(profname__icontains=value)

    requires = CharFilter(Course.objects,
                                  label='Requires Course',
                                  method='filter_requires_course',
                                  distinct=True,
                          )


    def filter_requires_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat('courses_required__major__abbreviation',
                                             Value('-'),
                                             'courses_required__catalogNumber',
                                             Value(' '),
                                             'courses_required__title')).filter(slug__icontains=value).values('abbreviation').annotate(pk=F('abbreviation')).distinct()

    class Meta:
        model = Major
        fields = [
            'abbreviation',
            'name',
            'description',
            'professors',
            'requires'
        ]
# this is useful for the ModelChoice version of professor
#    def __init__(self, *args, **kwargs):
#        super(MajorFilter, self).__init__(*args, **kwargs)
#        self.filters['professors'].extra.update(
#            {'empty_label': 'Has Professor'})
