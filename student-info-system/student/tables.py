import django_tables2 as tables

from sis.models import *


class GradesTable(tables.Table):
    section = tables.Column(attrs={'th': {'class': 'cscol'}, 'td': {'class': 'cscell'}})
    student = tables.Column(attrs={'th': {'class': 'cncol'}, 'td': {'class': 'cncell'}})
    grade = tables.Column(attrs={'th': {'class': 'cnncol'}, 'td': {'class': 'cnncell'}})
    status = tables.Column(attrs={'th': {'class': 'chcol'}, 'td': {'class': 'chcell'}})

    class Meta:
        model = SectionStudent
        template_name = "django_tables2/bootstrap.html"
        fields = ('section', 'student', 'grade', 'status')
        attrs = {"class": 'grades_table'}
        row_attrs = {'class': 'grades_row', 'data-id': lambda record: record.pk}