import django_tables2 as tables
from django.contrib.auth.models import User
from sis.models import *

# from sis.models import Major, Course, Professor


# For User names we want to show the full name ("first last") but sort by "last, first"
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


class MajorsTable(tables.Table):
    abbreviation = tables.Column(attrs={
        'th': {
            'style': 'text-align: center;'
        },
        'td': {
            'align': 'center'
        }
    })
    name = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    description = tables.Column(attrs={'th': {'style': 'text-align: center;'}})

    class Meta:
        model = Major
        template_name = "django_tables2/bootstrap.html"
        fields = ('abbreviation', 'name', 'description')
        row_attrs = {'class': 'mrow', 'data-id': lambda record: record.pk}


class BasicProfsTable(tables.Table):
    name = NameColumn(attrs={'th': {'style': 'text-align: center;'}})
    username = tables.Column(attrs={'th': {'style': 'text-align: center;'}})

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ('username', 'name')
        attrs = {"class": 'bprof'}
        row_attrs = {'class': 'prow', 'data-id': lambda record: record.pk}


class BasicCoursesTable(tables.Table):
    major = tables.Column(attrs={
        'th': {
            'style': 'text-align: center;'
        },
        'td': {
            'align': 'center'
        }
    })
    catalogNumber = tables.Column(verbose_name='Number',
                                  attrs={
                                      'th': {
                                          'style': 'text-align: center;'
                                      },
                                      'td': {
                                          'align': 'center'
                                      }
                                  })
    title = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    credits_earned = tables.Column(attrs={
        'th': {
            'style': 'text-align: center;'
        },
        'td': {
            'align': 'center'
        }
    })

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalogNumber', 'title', 'credits_earned')
        attrs = {"class": 'bcourse'}
        row_attrs = {'class': 'crow', 'data-id': lambda record: record.pk}


class SemestersTable(tables.Table):
    semester = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    year = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    date_started = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    date_ended = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    date_registration_opens = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    date_last_drop = tables.Column(attrs={'th': {'style': 'text-align: center;'}})

    class Meta:
        model = Semester
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'year', 'date_started', 'date_ended', 'date_registration_opens',
                  'date_last_drop')

        row_attrs = {'class': 'urow', 'data-id': lambda record: record.pk}
