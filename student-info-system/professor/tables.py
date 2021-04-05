import django_tables2 as tables
from sis.models import *


class SectionsTable(tables.Table):
    semester = tables.Column(attrs={'th': {'class': 'cscol'}, 'td': {'class': 'cscell'}})
    course = tables.Column(attrs={'th': {'class': 'cncol'}, 'td': {'class': 'cncell'}})
    number = tables.Column(attrs={'th': {'class': 'cnncol'}, 'td': {'class': 'cnncell'}})
    hours = tables.Column(attrs={'th': {'class': 'chcol'}, 'td': {'class': 'chcell'}})
    capacity = tables.Column(attrs={'th': {'class': 'cccol'}, 'td': {'class': 'cccell'}})

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'course', 'number', 'hours', 'capacity')
        row_attrs = {'class': 'srow', 'data-id': lambda record: record.pk}
