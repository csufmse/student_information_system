from django import forms
from django_filters import (CharFilter, ChoiceFilter, FilterSet, ModelChoiceFilter)
import django_tables2 as tables

from sis.models import (SectionStudent, Section, Semester, Major)

from sis.elements.utils import *


class SectionStudentFilter(FilterSet):
    semester = CharFilter(label='Semester', method='filter_semester')

    def filter_semester(self, queryset, name, value):
        return queryset.annotate(slug=Concat('section__semester__session',
                                             Value('-'),
                                             'section__semester__year',
                                             output_field=CharField())).filter(
                                                 slug__icontains=value)

    sec_status = ChoiceFilter(choices=Section.STATUSES,
                              field_name='section__status',
                              label="Section Status")
    student_status = ChoiceFilter(choices=SectionStudent.STATUSES,
                                  field_name='status',
                                  label="Student Status")
    grade = ChoiceFilter(choices=SectionStudent.GRADES, field_name='grade', label="Grade")

    def __init__(self, *args, **kwargs):
        super(SectionStudentFilter, self).__init__(*args, **kwargs)
        self.filters['sec_status'].extra.update({'empty_label': 'Any Section Status'})
        self.filters['student_status'].extra.update({'empty_label': 'Any Student Status'})
        self.filters['grade'].extra.update({'empty_label': 'Any Grade'})

    class Meta:
        model = SectionStudent
        fields = ['semester', 'sec_status', 'student_status', 'grade']


class StudentHistoryFilter(FilterSet):
    semester = CharFilter(label='Semester', method='filter_semester')
    major = ModelChoiceFilter(queryset=Major.objects,
                              field_name='section__course__major',
                              label='Major')

    def filter_semester(self, queryset, name, value):
        return queryset.annotate(slug=Concat('section__semester__session',
                                             Value('-'),
                                             'section__semester__year',
                                             output_field=CharField())).filter(
                                                 slug__icontains=value)

    student_status = ChoiceFilter(choices=SectionStudent.STATUSES,
                                  field_name='status',
                                  label="Student Status")
    grade = ChoiceFilter(choices=SectionStudent.GRADES, field_name='grade', label="Grade")

    def __init__(self, *args, **kwargs):
        super(StudentHistoryFilter, self).__init__(*args, **kwargs)
        self.filters['student_status'].extra.update({'empty_label': 'Any Status'})
        self.filters['grade'].extra.update({'empty_label': 'Any Grade'})
        self.filters['major'].extra.update({'empty_label': 'Any Major'})

    class Meta:
        model = SectionStudent
        fields = ['semester', 'major', 'student_status', 'grade']


class DropRequestForm(forms.Form):
    student_section = SectionStudentChoiceField(queryset=SectionStudent.objects.none(),
                                                required=True)
    reason = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        fields = ('student_section', 'reason')

    def __init__(self, *args, **kwargs):
        sectionstudent_qs = kwargs.pop('sectionstudent_qs', None)
        super(DropRequestForm, self).__init__(*args, **kwargs)
        self.fields['student_section'].queryset = sectionstudent_qs


# for when the student is known
class StudentHistoryTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='section__semester__name')
    section = ClassyColumn(css_class_base='section_name',
                           accessor='section__name',
                           order_by=('section__course__major__abbreviation',
                                     'section__course__catalog_number'))
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
        row_attrs = {'class': 'sectionstudent_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'sectionstudent_table'}


# for when the class is known
class StudentInSectionTable(tables.Table):
    username = ClassyColumn(accessor='student__profile__user__username',
                            css_class_base='username')
    name = ClassyColumn(accessor='student__profile__user__get_full_name',
                        css_class_base='user_name',
                        order_by=('student__profile__user__last_name',
                                  'student__profile__user__first_name'))
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
        row_attrs = {'class': 'sectionstudent_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'sectionstudent_table'}
