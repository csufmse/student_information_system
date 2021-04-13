from django.db.models import Value
from django.db.models.functions import Concat
from django_filters import (CharFilter, ChoiceFilter, FilterSet)

from sis.models import (Course, ReferenceItem)


class ItemFilter(FilterSet):
    course = CharFilter(Course.objects, label='Course Info', method='filter_course')

    def filter_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'course__major__abbreviation',
            Value('-'),
            'course__catalog_number',
            Value(' '),
            'course__title',
        )).filter(slug__icontains=value)

    type = ChoiceFilter(choices=ReferenceItem.TYPES, field_name='type', label="Type")

    title = CharFilter(field_name='title', lookup_expr='icontains')
    description = CharFilter(field_name='description', lookup_expr='icontains')
    link = CharFilter(field_name='link', lookup_expr='icontains')

    def __init__(self, *args, **kwargs):
        super(ItemFilter, self).__init__(*args, **kwargs)
        self.filters['type'].extra.update({'empty_label': 'Any Type'})

    class Meta:
        model = ReferenceItem
        fields = ['course', 'type', 'title', 'description', 'link']
