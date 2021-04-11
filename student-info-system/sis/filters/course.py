from django.db.models import Value
from django.db.models.functions import Concat
from django_filters import (CharFilter, FilterSet,
                            ModelChoiceFilter, ChoiceFilter, RangeFilter)

from sis.models import (Course, CoursePrerequisite, Major, Message, Professor, Section, Semester,
                        Student, SectionStudent, Profile)

class CourseFilter(FilterSet):
    major = ModelChoiceFilter(queryset=Major.objects, field_name='major', label='Major')

    catalog_number = RangeFilter(field_name='catalog_number')
    title = CharFilter(field_name='title', label='Title contains', lookup_expr='icontains')
    description = CharFilter(field_name='description',
                             label='Description contains',
                             lookup_expr='icontains')

    credits_earned = RangeFilter(label='Credits')

    # need filters for...
    prereqs = CharFilter(
        Course.objects,
        label='Has Prereq',
        method='filter_requires_course',
        distinct=True,
    )

    is_prereq = CharFilter(CoursePrerequisite.objects,
                           label='Is Prereq for',
                           method='filter_required_by')

    def filter_requires_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'prereqs__major__abbreviation',
            Value('-'),
            'prereqs__catalog_number',
            Value(' '),
            'prereqs__title',
        )).filter(slug__icontains=value)

    def filter_required_by(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'a_prerequisite__course__major__abbreviation',
            Value('-'),
            'a_prerequisite__course__catalog_number',
            Value(' '),
            'a_prerequisite__course__title',
        )).filter(slug__icontains=value)

    class Meta:
        model = Course
        fields = [
            'major', 'catalog_number', 'title', 'description', 'prereqs', 'is_prereq',
            'credits_earned'
        ]

    def __init__(self, *args, **kwargs):
        super(CourseFilter, self).__init__(*args, **kwargs)
        self.filters['major'].extra.update({'empty_label': 'Major...'})


class RequirementsCourseFilter(FilterSet):
    major = ModelChoiceFilter(queryset=Major.objects, field_name='major', label='Major')

    catalog_number = RangeFilter(field_name='catalog_number')
    title = CharFilter(field_name='title', label='Title contains', lookup_expr='icontains')
    credits_earned = RangeFilter(label='Credits')
    met = ChoiceFilter(label='Met?', choices=((True, 'Yes'), (False, 'No')))

    # need filters for...
    prereqs = CharFilter(
        Course.objects,
        label='Has Prereq',
        method='filter_requires_course',
        distinct=True,
    )

    is_prereq = CharFilter(CoursePrerequisite.objects,
                           label='Is Prereq for',
                           method='filter_required_by')

    def filter_requires_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'prereqs__major__abbreviation',
            Value('-'),
            'prereqs__catalog_number',
            Value(' '),
            'prereqs__title',
        )).filter(slug__icontains=value)

    def filter_required_by(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'a_prerequisite__course__major__abbreviation',
            Value('-'),
            'a_prerequisite__course__catalog_number',
            Value(' '),
            'a_prerequisite__course__title',
        )).filter(slug__icontains=value)

    class Meta:
        model = Course
        fields = [
            'major', 'catalog_number', 'title', 'prereqs', 'is_prereq',
            'credits_earned','met',
        ]

    def __init__(self, *args, **kwargs):
        super(RequirementsCourseFilter, self).__init__(*args, **kwargs)
        self.filters['met'].extra.update({'empty_label': 'Met?'})
        self.filters['major'].extra.update({'empty_label': 'Major...'})


