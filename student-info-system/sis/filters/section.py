from django.db.models import CharField, Value, F
from django.db.models.functions import Concat
from django_filters import (
    CharFilter,
    ChoiceFilter,
    FilterSet,
)

from sis.models import (Course, Section, Semester)


class SectionFilter(FilterSet):
    semester = CharFilter(Semester.objects, label='Semester', method='filter_semester')

    professor = CharFilter(label='Professor Name Contains', method='filter_professor')

    course_descr = CharFilter(Course.objects, label='Course Info', method='filter_course')

    hours = CharFilter(field_name='hours', lookup_expr='icontains')

    location = CharFilter(field_name='location', lookup_expr='icontains')

    status = ChoiceFilter(choices=Section.STATUSES, field_name='status')

    # seats_remaining = RangeFilter()

    def filter_semester(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'semester__session', Value('-'), 'semester__year', output_field=CharField())).filter(
                slug__icontains=value)

    def filter_professor(self, queryset, name, value):
        return queryset.annotate(slug=Concat('professor__profile__user__first_name',
                                             Value(' '),
                                             'professor__profile__user__last_name',
                                             output_field=CharField())).filter(
                                                 slug__icontains=value)

    def filter_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat('course__major__abbreviation', Value('-'),
                                            'course__catalog_number', Value(': '),
                                            'course__title',
                                             output_field=CharField())).filter(
                                                slug__icontains=value)

    def __init__(self, *args, **kwargs):
        super(SectionFilter, self).__init__(*args, **kwargs)
        self.filters['status'].extra.update({'empty_label': 'Any Status'})

    class Meta:
        model = Section
        fields = ['semester', 'course_descr', 'professor', 'hours', 'location', 'status']
