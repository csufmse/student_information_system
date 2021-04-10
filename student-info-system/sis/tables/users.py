import django_tables2 as tables

from sis.models import User
from sis.tables import *


class FullUsersTable(tables.Table):
    name = NameColumn(css_class_base='user_name')
    username = ClassyColumn(css_class_base='username')
    student_major = ClassyColumn(verbose_name='Student Major',
                                 css_class_base='major',
                                 accessor='profile__student__major__abbreviation')
    professor_department = ClassyColumn(verbose_name='Professor Dept',
                                        css_class_base='major',
                                        accessor='profile__professor__major__abbreviation')
    is_active = AbilityColumn(null=False, attrs=field_css_classes('active'))
    access_role = ClassyColumn(verbose_name='User Role',
                               accessor='profile__rolename',
                               css_class_base='role')
    class_level = ClassyColumn(verbose_name='Class',
                               css_class_base='classlevel',
                               accessor='profile__student__class_level')
    student_gpa = ClassyColumn(verbose_name='GPA',
                               accessor='profile__student__gpa',
                               css_class_base='gpa')

    def render_student_gpa(self, value):
        return '{:0.2f}'.format(value)

    credits_earned = ClassyColumn(
        verbose_name='Credits',
        css_class_base='credits',
        accessor='profile__student__credits_earned',
    )

    class Meta:
        attrs = {"class": 'fulluser_table'}
        fields = ('username', 'name', 'student_major', 'student_gpa', 'credits_earned',
                  'class_level', 'professor_department', 'access_role', 'is_active')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class UsersTable(FullUsersTable):
    name = NameColumn(css_class_base='user_name')
    username = ClassyColumn(css_class_base='username')

    class Meta:
        attrs = {"class": 'user_table'}
        exclude = ('student_major', 'student_gpa', 'credits_earned', 'class_level',
                   'professor_department', 'access_role', 'is_active')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class StudentsTable(tables.Table):
    name = NameColumn(css_class_base='user_name')
    username = ClassyColumn(css_class_base='username')
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
        fields = ('username', 'name', 'student_major', 'student_gpa', 'credits_earned',
                  'class_level', 'is_active')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class StudentInMajorTable(tables.Table):
    name = NameColumn(css_class_base='user_name')
    username = ClassyColumn(css_class_base='username')
    is_active = AbilityColumn(null=False, attrs=field_css_classes('active'))
    class_level = ClassyColumn(verbose_name='Class',
                               css_class_base='classlevel',
                               accessor='profile__student__class_level')
    gpa = ClassyColumn(verbose_name='GPA', css_class_base='gpa', accessor='profile__student__gpa')

    def render_gpa(self, value):
        return '{:0.2f}'.format(value)

    credits_earned = ClassyColumn(
        verbose_name='Credits',
        css_class_base='credits',
        accessor='profile__student__credits_earned',
    )

    class Meta:
        attrs = {"class": 'studentmajor_table'}
        fields = ('username', 'name', 'gpa', 'credits_earned', 'class_level')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"
