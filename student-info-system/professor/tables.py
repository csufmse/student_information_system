import django_tables2 as tables

from sis.models import *
from sis.tables import *


class SectionsTable(tables.Table):
    semester = tables.Column(attrs={'th': {'class': 'cscol'}, 'td': {'class': 'cscell'}})
    course = tables.Column(attrs={'th': {'class': 'cncol'}, 'td': {'class': 'cncell'}})
    number = tables.Column(attrs={'th': {'class': 'cnncol'}, 'td': {'class': 'cnncell'}})
    hours = tables.Column(attrs={'th': {'class': 'chcol'}, 'td': {'class': 'chcell'}})
    capacity = tables.Column(attrs={'th': {'class': 'cccol'}, 'td': {'class': 'cccell'}})
    location = tables.Column(attrs={'th': {'class': 'location'}, 'td': {'class': 'location'}})

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'course', 'number', 'hours', 'capacity', 'location')
        row_attrs = {'class': 'srow', 'data-id': lambda record: record.pk}


class StudentsTable(tables.Table):
    name = NameColumn(css_class_base='user_name')
    student_major = ClassyColumn(verbose_name='Student Major',
                                 css_class_base='major',
                                 accessor='profile__student__major__abbreviation')
    is_active = AbilityColumn(null=False, attrs=field_css_classes('active'))
    class_level = ClassyColumn(verbose_name='Class',
                               css_class_base='classlevel',
                               accessor='profile__student__class_level')
    student_gpa = ClassyColumn(verbose_name='GPA',
                               css_class_base='gpa',
                               accessor='profile__student__gpa')

    def render_student_gpa(self, value):
        return '{:0.2f}'.format(value)

    credits_earned = ClassyColumn(
        verbose_name='Credits',
        css_class_base='credits',
        accessor='profile__student__credits_earned',
    )

    class Meta:
        attrs = {"class": 'students_table'}
        model = User
        fields = ('name', 'student_major', 'student_gpa', 'credits_earned', 'class_level',
                  'is_active')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"
