import django_tables2 as tables

from sis.models import Course
from sis.tables import *


class CoursesTable(tables.Table):
    major = ClassyColumn(css_class_base='major', accessor='major__abbreviation')
    catalog_number = ClassyColumn(verbose_name='Catalog Number', css_class_base='catnumber')
    title = ClassyColumn(css_class_base='coursetitle')
    credits_earned = ClassyColumn(css_class_base='credits')

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalog_number', 'title', 'credits_earned')
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'course_table'}


# when the major is known
class CoursesForMajorTable(tables.Table):
    catalog_number = ClassyColumn(verbose_name='Catalog Number', css_class_base='catnumber')
    title = ClassyColumn(css_class_base='coursetitle')
    credits_earned = ClassyColumn(css_class_base='credits')

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('catalog_number', 'title', 'credits_earned')
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'course_table'}


# for list of course with "met?" flag
class MajorCoursesMetTable(tables.Table):
    major = ClassyColumn(css_class_base='major', accessor='major__abbreviation')
    catalog_number = ClassyColumn(verbose_name='Catalog Number', css_class_base='catnumber')
    title = ClassyColumn(css_class_base='coursetitle')
    credits_earned = ClassyColumn(css_class_base='credits')
    met = ClassyBooleanColumn(css_class_base='met')

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalog_number', 'title', 'credits_earned', 'met')
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'majorcourse_table'}


