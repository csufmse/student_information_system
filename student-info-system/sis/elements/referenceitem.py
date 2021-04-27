from django.db.models import Value
from django.db.models.functions import Concat
from django_filters import (CharFilter, ChoiceFilter, FilterSet)
from django import forms

import django_tables2 as tables

from sis.models import (Course, ReferenceItem)

from sis.elements.utils import *


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


class ReferenceItemForm(forms.ModelForm):

    class Meta:
        model = ReferenceItem
        fields = ['title', 'description', 'link', 'edition', 'isbn', 'type']


class ReferenceItemCreationForm(forms.ModelForm):
    type = forms.ChoiceField(choices=ReferenceItem.TYPES)
    type.widget.attrs.update({'class': 'type_sel selectpicker'})

    course = forms.ModelChoiceField(queryset=Course.objects.all())
    course.widget.attrs.update({'class': 'course_sel selectpicker'})

    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256,
                                  widget=forms.Textarea(attrs={'rows': 3}),
                                  required=False)
    link = forms.CharField(max_length=256, required=False)
    edition = forms.CharField(max_length=256, required=False)

    class Meta:
        model = ReferenceItem
        fields = ('type', 'course', 'title', 'description', 'link', 'edition')

    def __init__(self, *args, **kwargs):
        super(ReferenceItemCreationForm, self).__init__(*args, **kwargs)

        # we defer loading of courses until we know what major is chosen
        if 'initial' in kwargs:
            major = kwargs['initial']['professor'].major
            if major:
                self.fields['course'].queryset = Course.objects.filter(major=major)
        elif 'instance' in kwargs:
            major = kwargs['instance'].professor.major
            if major:
                self.fields['course'].queryset = Course.objects.filter(major=major)


class ProfReferenceItemsTable(tables.Table):
    course = ClassyColumn(css_class_base='course',
                          accessor='course__name',
                          order_by=('course__major__abbreviation', 'course__catalog_number'))
    type = ClassyColumn(verbose_name='Type', css_class_base='item_type')
    title = ClassyColumn(css_class_base='item_title')
    link = tables.TemplateColumn(
        '{% if record.link %}<a href="{{record.link}}" target="_blank">' +
        '{{record.link}}</a>{% endif %}')
    edition = ClassyColumn(css_class_base='item_edition')
    description = ClassyColumn(css_class_base='item_description')

    class Meta:
        model = ReferenceItem
        template_name = "django_tables2/bootstrap.html"
        fields = ('course', 'type', 'title', 'edition', 'description', 'link')
        row_attrs = {'class': 'refitem_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'items_table'}
