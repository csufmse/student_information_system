import django_tables2 as tables

from django_filters import (CharFilter, ChoiceFilter, FilterSet, RangeFilter)

from sis.models import (SectionReferenceItem, ReferenceItem)

from sis.elements.utils import *


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


class SectionReferenceItemsTable(tables.Table):
    section = ClassyColumn(css_class_base='sectionumber',
                           accessor='section__name',
                           order_by=('course__major__abbreviation', 'course__catalog_number'))
    course = ClassyColumn(css_class_base='coursename', accessor='section__course__title')
    semester = ClassyColumn(accessor='section__semester', css_class_base='semester')
    professor = ClassyColumn(accessor='section__professor', css_class_base='user_name')
    index = ClassyColumn(verbose_name="#", css_class_base='item_index')
    type = ClassyColumn(verbose_name='Type', css_class_base='item_type', accessor='item__type')
    title = ClassyColumn(css_class_base='item_title', accessor='item__title')
    link = tables.TemplateColumn(
        '{% if record.item.link %}<a href="{{record.item.link}}" target="_blank">' +
        '{{record.item.link}}</a>{% endif %}')
    edition = ClassyColumn(css_class_base='item_edition', accessor='item__edition')
    description = ClassyColumn(css_class_base='item_description', accessor='item__description')

    class Meta:
        model = SectionReferenceItem
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'section', 'course', 'professor', 'index', 'type', 'title',
                  'edition', 'description', 'link')
        row_attrs = {'class': 'secitem_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'secitems_table'}


class ReferenceItemsForSectionTable(SectionReferenceItemsTable):

    class Meta:
        template_name = "django_tables2/bootstrap.html"
        exclude = ('section', 'semester', 'professor')
        row_attrs = {'class': 'secitem_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'secitems_table'}
