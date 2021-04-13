import django_tables2 as tables

from sis.models import SectionStudent
from sis.tables import *


# for when the student is known
class StudentHistoryTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='section__semester__name')
    section = ClassyColumn(css_class_base='section_name', accessor='section__name')
    major = ClassyColumn(accessor='section__course__major', css_class_base='major')
    title = ClassyColumn(accessor='section__course__title', css_class_base='coursetitle')
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
    professor = ClassyColumn(accessor='section__professor',
                             order_by=("section__professor__profile__user__last_name",
                                       "section__professor__profile__user__first_name"),
                             css_class_base='username')

    class Meta:
        model = SectionStudent
        fields = ('semester', 'major', 'section', 'title', 'professor', 'credits_earned',
                  'status', 'letter_grade')
        template_name = "django_tables2/bootstrap.html"
        row_attrs = {
            'class': 'sectionstudent_row',
            'data-id': lambda record: record.student.profile.user.pk
        }
        attrs = {"class": 'sectionstudent_table'}


# shows all info: semester, course, section, student
class SectionStudentsTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='name',
                            order_by=('semester.year','semester.session_order'))
    course = ClassyColumn(accessor='course', css_class_base='course')
    username = ClassyColumn(accessor='student__profile__user__username',
                            css_class_base='username')
    name = ClassyColumn(accessor='student__profile__name', css_class_base='user_name',
                        order_by=('student__profile__user__last_name', 'student__profile__user__first_name'))
    major = ClassyColumn(accessor='student__profile__major__abbreviation', css_class_base='major')
    sec_status = ClassyColumn(
        verbose_name="Section Status",
        css_class_base='sectionstatus',
        accessor='section__status',
    )
    stud_status = ClassyColumn(
        verbose_name="Student Status",
        css_class_base='sectionstudentstatus',
        accessor='status',
    )
    letter_grade = ClassyColumn(verbose_name="Grade",
                                accessor='grade',
                                css_class_base='lettergrade')

    class Meta:
        model = SectionStudent
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'course', 'username', 'name', 'major', 'sec_status', 'stud_status',
                  'letter_grade')
        row_attrs = {
            'class': 'sectionstudent_row',
            'data-id': lambda record: record.student.profile.user.pk
        }
        attrs = {"class": 'sectionstudent_table'}


# for when the class is known
class StudentInSectionTable(tables.Table):
    username = ClassyColumn(accessor='student__profile__user__username',
                            css_class_base='username')
    name = ClassyColumn(accessor='student__profile__user__name', css_class_base='user_name')
    major = ClassyColumn(accessor='student__major__abbreviation', css_class_base='major')
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
            'data-id': lambda record: record.student.profile.user.pk
        }
        attrs = {"class": 'sectionstudent_table'}
