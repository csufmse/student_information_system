import django_tables2 as tables

from sis.models import Section
from sis.tables import *


class SectionsTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='semester',
                            order_by=('semester.semester_order'))
    course = ClassyColumn(css_class_base='course', accessor='course__name')
    number = ClassyColumn(css_class_base='section_number')
    status = ClassyColumn(css_class_base='sectionstatus')
    course_title = ClassyColumn(css_class_base='coursetitle')
    hours = ClassyColumn(css_class_base='hours')
    location = ClassyColumn(css_class_base='location')
    professor = ClassyColumn(css_class_base='user_name', accessor='professor__profile__name')
    capacity = ClassyColumn(css_class_base='capac')
    seats_remaining = ClassyColumn(css_class_base='remaining')

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'course', 'number', 'status', 'course_title', 'hours', 'location',
                  'professor', 'capacity', 'seats_remaining')
        row_attrs = {'class': 'section_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'section_table'}


class ProfSectionsTable(SectionsTable):

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        exclude = ('status', 'course_title', 'professor', 'seats_remaining')
        row_attrs = {'class': 'srow', 'data-id': lambda record: record.pk}


# for when Class is known
class SectionForClassTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='semester__name',
                            order_by=('semester_order'))
    section = ClassyColumn(css_class_base='section_name', accessor='name')
    status = ClassyColumn(css_class_base='sectionstatus')
    hours = ClassyColumn(css_class_base='hours')
    location = ClassyColumn(css_class_base='location')
    professor = ClassyColumn(css_class_base='username', accessor='professor__profile__name')
    capacity = ClassyColumn(css_class_base='capac')
    seats_remaining = ClassyColumn(css_class_base='remaining')

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'section', 'status', 'hours', 'location', 'professor', 'capacity',
                  'seats_remaining')
        row_attrs = {'class': 'section_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'section_table'}
