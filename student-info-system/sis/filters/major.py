from django.db.models import Value
from django.db.models.functions import Concat
from django_filters import (
    CharFilter,
    FilterSet,
)

from sis.models import (Course, CoursePrerequisite, Major, Message, Professor, Section, Semester,
                        Student, SectionStudent, Profile, ReferenceItem, SectionReferenceItem)


class MajorFilter(FilterSet):
    abbreviation = CharFilter(field_name='abbreviation', lookup_expr='icontains')
    title = CharFilter(field_name='title', label='Title contains', lookup_expr='icontains')
    description = CharFilter(field_name='description',
                             label='Description contains',
                             lookup_expr='icontains')
    # this version lets them type part of the profs name
    professors = CharFilter(field_name='professor__profile__user__last_name',
                            lookup_expr='icontains',
                            label='Has Professor Name')
    # this version lets them pick professors
    #    professors = ModelChoiceFilter(queryset=Professor.objects,
    #                                  method='filter_has_prof',
    #                                  label='Has Professor')
    #    def filter_has_prof(self, queryset, name, value):
    #        return queryset.annotate(profname=Concat('professor__user__first_name',Value(' '),
    #                                                 'professor__user__last_name')).filter(profname__icontains=value)

    requires = CharFilter(
        Course.objects,
        label='Requires Course',
        method='filter_requires_course',
        distinct=True,
    )

    def filter_requires_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat('courses_required__major__abbreviation', Value(
            '-'), 'courses_required__catalog_number', Value(
                ' '), 'courses_required__title')).filter(slug__icontains=value).distinct()

    class Meta:
        model = Major
        fields = ['abbreviation', 'title', 'description', 'professors', 'requires']

        def __init__(self, *args, **kwargs):
            super(MajorFilter, self).__init__(*args, **kwargs)
            self.filters['abbreviation'].extra.update({'empty_label': 'Any Major/Department...'})
