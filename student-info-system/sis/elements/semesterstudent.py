from django_filters import CharFilter, FilterSet
from django.db.models import CharField, Value
from django.db.models.functions import Concat

import django_tables2 as tables

from sis.models import SemesterStudent

from sis.elements.utils import *


class SemesterStudentFilter(FilterSet):
    semester = CharFilter(SemesterStudent.objects, label='Semester', method='filter_semester')

    def filter_semester(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'semester__session', Value('-'), 'semester__year', output_field=CharField())).filter(
                slug__icontains=value)

    class Meta:
        model = SemesterStudent
        fields = ['semester']


class SemesterStudentSummaryTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='semester__name',
                            order_by=('semester__year', 'semester__session_order'))
    gpa = ClassyColumn(verbose_name='GPA', css_class_base='gpa', accessor='gpa')

    def render_gpa(self, value):
        return '{:0.2f}'.format(value)

    credits_attempted = ClassyColumn(verbose_name='Credits Attempted',
                                     css_class_base='credits',
                                     accessor='credits_attempted')
    credits_earned = ClassyColumn(verbose_name='Credits Earned',
                                  css_class_base='credits',
                                  accessor='credits_earned')

    class Meta:
        model = SemesterStudent
        template_name = "django_tables2/bootstrap.html"
        fields = ['semester', 'gpa', 'credits_attempted', 'credits_earned']
        attrs = {"class": 'semesterstudents_table'}
        row_attrs = {'class': 'semesterstudent_row', 'data-id': lambda record: record.pk}
