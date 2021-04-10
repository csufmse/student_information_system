import django_tables2 as tables

from sis.models import ReferenceItem
from sis.tables import *


class ProfReferenceItemsTable(tables.Table):
    course = ClassyColumn(css_class_base='course', accessor='course__name')
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
