from django_filters import (CharFilter, ChoiceFilter, FilterSet, RangeFilter)

from sis.models import (SectionReferenceItem, ReferenceItem)


class SectionItemFilter(FilterSet):

    index = RangeFilter(field_name='index')
    type = ChoiceFilter(choices=ReferenceItem.TYPES, field_name='item__type', label="Type")

    title = CharFilter(field_name='item__title', lookup_expr='icontains')
    description = CharFilter(field_name='item__description', lookup_expr='icontains')
    link = CharFilter(field_name='item__link', lookup_expr='icontains')

    def __init__(self, *args, **kwargs):
        super(SectionItemFilter, self).__init__(*args, **kwargs)
        self.filters['type'].extra.update({'empty_label': 'Any Type'})

    class Meta:
        model = SectionReferenceItem
        fields = ['index', 'type', 'title', 'description', 'link']
