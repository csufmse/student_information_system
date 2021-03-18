from django.db.models import Count, F, Value
from django.db.models.functions import Concat
import django_tables2 as tables
from django.contrib.auth.models import User


class NameColumn(tables.Column):

    def render(self, record):
        return record.name

    def order(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "name_sort")
        return (queryset, True)


class AbilityColumn(tables.BooleanColumn):
    header = "Enabled?"


class UsersTable(tables.Table):
    username = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    name = NameColumn(attrs={'th': {'style': 'text-align: center;'}})
    is_active = AbilityColumn(null=False,
                              attrs={
                                  'th': {
                                      'style': 'text-align: center;'
                                  },
                                  'td': {
                                      'align': 'center'
                                  }
                              })
    access_role = tables.Column(attrs={
        'th': {
            'style': 'text-align: center;'
        },
        'td': {
            'align': 'center'
        }
    })

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ("username", "name", "access_role", "is_active")

        row_attrs = {'class': 'urow', 'data-id': lambda record: record.pk}
