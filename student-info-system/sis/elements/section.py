from datetime import date

from django import forms
from django.db.models import CharField, Value, F
from django.db.models.functions import Concat
import django_tables2 as tables
from django_filters import (CharFilter, ChoiceFilter, FilterSet)

from sis.models import (
    Course,
    CoursePrerequisite,
    Major,
    Professor,
    Section,
    SectionStudent,
    Profile,
    Semester,
    UpperField,
)

from sis.elements.utils import *


class SectionFilter(FilterSet):
    semester = CharFilter(Semester.objects, label='Semester', method='filter_semester')

    professor = CharFilter(label='Professor Name Contains', method='filter_professor')

    course_descr = CharFilter(Course.objects, label='Course Info', method='filter_course')

    hours = CharFilter(field_name='hours', lookup_expr='icontains')

    location = CharFilter(field_name='location', lookup_expr='icontains')

    status = ChoiceFilter(choices=Section.STATUSES, field_name='status')

    graduate = ChoiceFilter(field_name='course__graduate',
                            label='Course Level?',
                            choices=((True, 'Graduate'), (False, 'Undergrad')))

    # seats_remaining = RangeFilter()

    def filter_semester(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'semester__session', Value('-'), 'semester__year', output_field=CharField())).filter(
                slug__icontains=value)

    def filter_professor(self, queryset, name, value):
        return queryset.annotate(slug=Concat('professor__profile__user__first_name',
                                             Value(' '),
                                             'professor__profile__user__last_name',
                                             output_field=CharField())).filter(
                                                 slug__icontains=value)

    def filter_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat('course__major__abbreviation',
                                             Value('-'),
                                             'course__catalog_number',
                                             Value(': '),
                                             'course__title',
                                             output_field=CharField())).filter(
                                                 slug__icontains=value)

    def __init__(self, *args, **kwargs):
        super(SectionFilter, self).__init__(*args, **kwargs)
        self.filters['status'].extra.update({'empty_label': 'Any Status'})
        self.filters['graduate'].extra.update({'empty_label': 'Any Course Level'})

    class Meta:
        model = Section
        fields = [
            'semester', 'course_descr', 'graduate', 'professor', 'hours', 'location', 'status'
        ]


class SectionCreationForm(forms.ModelForm):
    semester = forms.ModelChoiceField(queryset=Semester.objects.filter(
        date_ended__gt=date.today()))
    semester.widget.attrs.update({'class': 'semester_sel selectpicker'})

    course = forms.ModelChoiceField(queryset=Course.objects.all())
    course.widget.attrs.update({'class': 'course_sel selectpicker'})

    hours = forms.CharField(max_length=100)

    location = forms.CharField(max_length=256, widget=forms.Textarea(attrs={'rows': 3}))

    professor = forms.ModelChoiceField(queryset=Professor.objects.all())
    professor.widget.attrs.update({'class': 'user_sel selectpicker'})

    capacity = forms.IntegerField()
    status = forms.ChoiceField(choices=Section.STATUSES)

    class Meta:
        model = Section
        fields = ('semester', 'course', 'hours', 'professor', 'capacity', 'location', 'status')


class SectionEditForm(forms.ModelForm):
    hours = forms.CharField(max_length=100)

    location = forms.CharField(max_length=256, widget=forms.Textarea(attrs={'rows': 3}))

    professor = forms.ModelChoiceField(queryset=Professor.objects.none())
    professor.widget.attrs.update({'class': 'user_sel selectpicker'})

    capacity = forms.IntegerField()
    status = forms.ChoiceField(choices=Section.STATUSES)

    class Meta:
        model = Section
        fields = ('hours', 'professor', 'capacity', 'location', 'status')

    def __init__(self, *args, **kwargs):
        super(SectionEditForm, self).__init__(*args, **kwargs)

        # we defer loading of professors until we know what major is chosen
        if kwargs['instance']:
            major = kwargs['instance'].course.major
            if major:
                self.fields['professor'].queryset = Professor.objects.filter(
                    profile__user__is_active=True, major=major)


class SectionsTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='semester',
                            order_by=('semester.year', 'semester.session_order'))
    course = ClassyColumn(css_class_base='course',
                          accessor='course__name',
                          order_by=('course__major__abbreviation', 'course__catalog_number'))
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
        row_attrs = {'class': 'section_row', 'data-id': lambda record: record.pk}


# for when Class is known
class SectionForClassTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='semester__name',
                            order_by=('semester.year', 'semester.session_order'))
    section = ClassyColumn(css_class_base='section_name',
                           accessor='name',
                           order_by=('course__major__abbreviation', 'course__catalog_number'))
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
