import django_tables2 as tables
from django.contrib.auth.models import User

from sis.models import *


# Each column and cell has its own CSS class based on the type of
# data in it.
def field_css_classes(field_name):
    return {'th': {'class': field_name + '_col'}, 'td': {'class': field_name + '_cell'}}


class ClassyColumn(tables.Column):

    def __init__(self, *args, **kwargs):
        if 'css_class_base' in kwargs:
            css_class_base = kwargs.pop('css_class_base', None)
            kwargs['attrs'] = field_css_classes(css_class_base)
        super(ClassyColumn, self).__init__(*args, **kwargs)


# For User names we want to show the full name ("first last") but sort by "last, first"
class NameColumn(ClassyColumn):

    def render(self, record):
        return record.name

    def order(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "name_sort")
        return (queryset, True)


class AbilityColumn(tables.BooleanColumn):
    header = "Enabled?"


class FullUsersTable(tables.Table):
    username = ClassyColumn(css_class_base='username')
    name = NameColumn(css_class_base='user_name')
    student_major = ClassyColumn(verbose_name='Student Major',
                                 css_class_base='major',
                                 accessor='student__major__abbreviation')
    professor_department = ClassyColumn(verbose_name='Professor Dept',
                                        css_class_base='major',
                                        accessor='professor__major__abbreviation')
    is_active = AbilityColumn(null=False, attrs=field_css_classes('active'))
    access_role = ClassyColumn(verbose_name='User Role', css_class_base='role')
    class_level = ClassyColumn(verbose_name='Class',
                               css_class_base='classlevel',
                               accessor='student__class_level')
    student_gpa = ClassyColumn(verbose_name='GPA', css_class_base='gpa', accessor='student__gpa')

    def render_student_gpa(self, value):
        return '{:0.2f}'.format(value)

    credits_earned = ClassyColumn(
        verbose_name='Credits',
        css_class_base='credits',
        accessor='student__credits_earned',
    )

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ('username', 'name', 'student_major', 'student_gpa', 'credits_earned',
                  'class_level', 'professor_department', 'access_role', 'is_active')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'fulluser_table'}


class StudentInMajorTable(tables.Table):
    username = ClassyColumn(css_class_base='username')
    name = NameColumn(css_class_base='user_name')
    is_active = AbilityColumn(null=False, attrs=field_css_classes('active'))
    class_level = ClassyColumn(verbose_name='Class',
                               css_class_base='classlevel',
                               accessor='student__class_level')
    gpa = ClassyColumn(verbose_name='GPA', css_class_base='gpa', accessor='student__gpa')

    def render_gpa(self, value):
        return '{:0.2f}'.format(value)

    credits_earned = ClassyColumn(
        verbose_name='Credits',
        css_class_base='credits',
        accessor='student__credits_earned',
    )

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ('username', 'name', 'gpa', 'credits_earned', 'class_level')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'studentmajor_table'}


class MajorsTable(tables.Table):
    abbreviation = ClassyColumn(css_class_base='major')
    name = ClassyColumn(css_class_base='majorname')
    description = ClassyColumn(css_class_base='majordescr')

    class Meta:
        model = Major
        template_name = "django_tables2/bootstrap.html"
        fields = ('abbreviation', 'name', 'description')
        row_attrs = {'class': 'major_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'major_table'}


class UsersTable(tables.Table):
    name = NameColumn(css_class_base='user_name')
    username = ClassyColumn(css_class_base='username')

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ('username', 'name')
        attrs = {"class": 'user_table'}
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}


class CoursesTable(tables.Table):
    major = ClassyColumn(css_class_base='major')
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


class SemestersTable(tables.Table):
    semester = ClassyColumn(verbose_name='Session', css_class_base='semester')
    year = ClassyColumn(css_class_base='year')
    date_registration_opens = ClassyColumn(verbose_name='Registration Opens',
                                           css_class_base='date')
    date_last_drop = ClassyColumn(verbose_name='Date of Last Drop', css_class_base='date')
    date_started = ClassyColumn(verbose_name='Start of Classes', css_class_base='date')
    date_ended = ClassyColumn(verbose_name='End of Classes', css_class_base='date')

    class Meta:
        model = Semester
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'year', 'date_registration_opens', 'date_started', 'date_last_drop',
                  'date_ended')
        attrs = {"class": 'semester_table'}
        row_attrs = {'class': 'semester_row', 'data-id': lambda record: record.pk}


class SemestersSummaryTable(tables.Table):
    year = ClassyColumn(verbose_name='Year', css_class_base='year')
    semester = ClassyColumn(verbose_name='Session', css_class_base='semester', accessor='name')

    class Meta:
        model = Semester
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'year',
            'semester',
        )
        attrs = {"class": 'semester_table'}
        row_attrs = {'class': 'semester_row', 'data-id': lambda record: record.pk}


class SectionsTable(tables.Table):
    semester = ClassyColumn(css_class_base='sem')
    course = ClassyColumn(css_class_base='course')
    number = ClassyColumn(css_class_base='secnum')
    status = ClassyColumn(css_class_base='sectionstatus')
    course_title = ClassyColumn(css_class_base='coursetitle')
    hours = ClassyColumn(css_class_base='hours')
    professor = ClassyColumn(css_class_base='user_name')
    capacity = ClassyColumn(css_class_base='capac')
    seats_remaining = ClassyColumn(css_class_base='remaining')

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'course', 'number', 'status', 'course_title', 'hours', 'professor',
                  'capacity', 'seats_remaining')
        row_attrs = {'class': 'section_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'section_table'}


# for when Class is known
class SectionForClassTable(tables.Table):
    semester = ClassyColumn(css_class_base='sem')
    status = ClassyColumn(css_class_base='sectionstatus')
    hours = ClassyColumn(css_class_base='hours')
    professor = ClassyColumn(css_class_base='user_name')
    capacity = ClassyColumn(css_class_base='capac')
    seats_remaining = ClassyColumn(css_class_base='remaining')

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'status', 'hours', 'professor', 'capacity', 'seats_remaining')
        row_attrs = {'class': 'section_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'section_table'}


# shows all info: semester, course, section, student
class SectionStudentsTable(tables.Table):
    semester = ClassyColumn(accessor='semester', css_class_base='semester')
    course = ClassyColumn(accessor='course', css_class_base='course')
    username = ClassyColumn(accessor='student__user__username', css_class_base='username')
    name = ClassyColumn(accessor='student__user__name', css_class_base='user_name')
    major = ClassyColumn(accessor='student__major', css_class_base='major')
    status = ClassyColumn(
        verbose_name="Status",
        css_class_base='sectionstatus',
        accessor='status',
    )
    letter_grade = ClassyColumn(verbose_name="Grade",
                                accessor='grade',
                                css_class_base='lettergrade')

    class Meta:
        model = SectionStudent
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'course', 'username', 'name', 'major', 'status', 'letter_grade')
        row_attrs = {
            'class': 'sectionstudent_row',
            'data-id': lambda record: record.student.user.pk
        }
        attrs = {"class": 'sectionstudent_table'}


# for when the class is known
class StudentInSectionTable(tables.Table):
    username = ClassyColumn(accessor='student__user__username', css_class_base='username')
    name = ClassyColumn(accessor='student__user__name', css_class_base='user_name')
    major = ClassyColumn(accessor='student__major', css_class_base='major')
    gpa = ClassyColumn(accessor='student__gpa', css_class_base='gpa')

    def render_gpa(self, value):
        return '{:0.2f}'.format(value)

    status = ClassyColumn(
        verbose_name="Status",
        css_class_base='sectionstatus',
        accessor='status',
    )
    letter_grade = ClassyColumn(verbose_name="Grade",
                                accessor='grade',
                                css_class_base='lettergrade')

    class Meta:
        model = SectionStudent
        template_name = "django_tables2/bootstrap.html"
        fields = ('username', 'name', 'major', 'gpa', 'status', 'letter_grade')
        row_attrs = {
            'class': 'sectionstudent_row',
            'data-id': lambda record: record.student.user.pk
        }
        attrs = {"class": 'sectionstudent_table'}


# for when the student is known
class StudentHistoryTable(tables.Table):
    semester = ClassyColumn(accessor='section__semester', css_class_base='semester')
    section = ClassyColumn(accessor='section', css_class_base='secnum')
    course_title = ClassyColumn(accessor='section__course__title', css_class_base='coursetitle')
    credits_earned = ClassyColumn(
        verbose_name='Credits',
        css_class_base='credits',
        accessor='section__course__credits_earned',
    )
    status = ClassyColumn(
        verbose_name="Status",
        css_class_base='sectionstatus',
        accessor='status',
    )
    letter_grade = ClassyColumn(verbose_name="Grade",
                                accessor='grade',
                                css_class_base='lettergrade')

    class Meta:
        model = SectionStudent
        fields = ('semester', 'section', 'course_title', 'credits_earned', 'status',
                  'letter_grade')
        template_name = "django_tables2/bootstrap.html"
        row_attrs = {
            'class': 'sectionstudent_row',
            'data-id': lambda record: record.student.user.pk
        }
        attrs = {"class": 'sectionstudent_table'}
