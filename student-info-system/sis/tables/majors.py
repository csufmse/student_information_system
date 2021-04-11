import django_tables2 as tables

from sis.models import Major
from sis.tables import *


class MajorsTable(tables.Table):
    abbreviation = ClassyColumn(css_class_base='major')
    name = ClassyColumn(css_class_base='majorname')
    description = ClassyColumn(css_class_base='majordescr')
    contact = ClassyColumn(css_class_base='username')

    class Meta:
        model = Major
        template_name = "django_tables2/bootstrap.html"
        fields = ('abbreviation', 'name', 'description', 'contact')
        row_attrs = {'class': 'major_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'major_table'}
