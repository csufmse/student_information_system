from django import forms
from django.core.validators import *
from django.db.models import Value
from django.db.models.functions import Concat
from django_filters import (CharFilter, FilterSet, ModelChoiceFilter, ChoiceFilter, RangeFilter)
import django_tables2 as tables

from sis.models import (Course, CoursePrerequisite, Major, Message, Professor, Section, Semester,
                        Student, SectionStudent, Profile)

from sis.elements.utils import *


class CourseFilter(FilterSet):
    major = ModelChoiceFilter(queryset=Major.objects, field_name='major', label='Major')

    catalog_number = RangeFilter(field_name='catalog_number')
    title = CharFilter(field_name='title', label='Title contains', lookup_expr='icontains')
    description = CharFilter(field_name='description',
                             label='Description contains',
                             lookup_expr='icontains')

    credits_earned = RangeFilter(label='Credits')
    graduate = ChoiceFilter(label='Course Level?',
                            choices=((True, 'Graduate'), (False, 'Undergrad')))

    # need filters for...
    prereqs = CharFilter(
        Course.objects,
        label='Has Prereq',
        method='filter_requires_course',
        distinct=True,
    )

    is_prereq = CharFilter(CoursePrerequisite.objects,
                           label='Is Prereq for',
                           method='filter_required_by')

    def filter_requires_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'prereqs__major__abbreviation',
            Value('-'),
            'prereqs__catalog_number',
            Value(' '),
            'prereqs__title',
        )).filter(slug__icontains=value)

    def filter_required_by(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'a_prerequisite__course__major__abbreviation',
            Value('-'),
            'a_prerequisite__course__catalog_number',
            Value(' '),
            'a_prerequisite__course__title',
        )).filter(slug__icontains=value)

    class Meta:
        model = Course
        fields = [
            'major', 'catalog_number', 'graduate', 'title', 'description', 'prereqs', 'is_prereq',
            'credits_earned'
        ]

    def __init__(self, *args, **kwargs):
        super(CourseFilter, self).__init__(*args, **kwargs)
        self.filters['major'].extra.update({'empty_label': 'Major...'})
        self.filters['graduate'].extra.update({'empty_label': 'Course Level...'})


class RequirementsCourseFilter(FilterSet):
    major = ModelChoiceFilter(queryset=Major.objects, field_name='major', label='Major')

    catalog_number = RangeFilter(field_name='catalog_number')
    title = CharFilter(field_name='title', label='Title contains', lookup_expr='icontains')
    credits_earned = RangeFilter(label='Credits')
    met = ChoiceFilter(label='Met?', choices=((True, 'Yes'), (False, 'No')))

    # need filters for...
    prereqs = CharFilter(
        Course.objects,
        label='Has Prereq',
        method='filter_requires_course',
        distinct=True,
    )

    is_prereq = CharFilter(CoursePrerequisite.objects,
                           label='Is Prereq for',
                           method='filter_required_by')

    def filter_requires_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'prereqs__major__abbreviation',
            Value('-'),
            'prereqs__catalog_number',
            Value(' '),
            'prereqs__title',
        )).filter(slug__icontains=value)

    def filter_required_by(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'a_prerequisite__course__major__abbreviation',
            Value('-'),
            'a_prerequisite__course__catalog_number',
            Value(' '),
            'a_prerequisite__course__title',
        )).filter(slug__icontains=value)

    class Meta:
        model = Course
        fields = [
            'major',
            'catalog_number',
            'title',
            'prereqs',
            'is_prereq',
            'credits_earned',
            'met',
        ]

    def __init__(self, *args, **kwargs):
        super(RequirementsCourseFilter, self).__init__(*args, **kwargs)
        self.filters['met'].extra.update({'empty_label': 'Met?'})
        self.filters['major'].extra.update({'empty_label': 'Major...'})


class CourseCreationForm(forms.ModelForm):
    major = forms.ModelChoiceField(queryset=Major.objects.all())
    major.widget.attrs.update({'class': 'major_sel selectpicker'})

    catalog_number = forms.IntegerField(label='Number', validators=(MinValueValidator(1),))
    title = forms.CharField(label='Title', max_length=256)
    description = forms.CharField(max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))
    credits_earned = forms.DecimalField(label='Credits', max_digits=2, decimal_places=1)
    graduate = forms.ChoiceField(label='Graduate',
                                 choices=((True, 'Graduate'), (False, 'Undergrad')))

    class Meta:
        model = Course
        fields = ('major', 'catalog_number', 'graduate', 'title', 'description', 'credits_earned')


class CourseEditForm(forms.ModelForm):
    major = forms.ModelChoiceField(queryset=Major.objects.all())
    major.widget.attrs.update({'class': 'major_sel selectpicker'})

    catalog_number = forms.IntegerField(label='Number', validators=(MinValueValidator(1),))
    title = forms.CharField(label='Title', max_length=256)
    description = forms.CharField(label='Description',
                                  max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))
    credits_earned = forms.DecimalField(label='Credits', max_digits=2, decimal_places=1)
    graduate = forms.ChoiceField(label='Graduate',
                                 choices=((True, 'Graduate'), (False, 'Undergrad')))

    prereqs = CourseChoiceField(queryset=Course.objects.all(),
                                widget=forms.CheckboxSelectMultiple,
                                required=False)

    class Meta:
        model = Course
        fields = ('major', 'catalog_number', 'graduate', 'title', 'description', 'credits_earned',
                  'prereqs')

    def __init__(self, *args, **kwargs):
        super(CourseEditForm, self).__init__(*args, **kwargs)
        # we defer loading of professors until we know what major is chosen
        if kwargs['instance']:
            the_course = kwargs['instance']
            if the_course:
                self.fields['prereqs'].queryset = Course.objects.exclude(id=the_course.id)

    def clean(self):
        cleaned_data = super().clean()
        are_valid = self.instance.are_candidate_prerequisites_valid(cleaned_data['prereqs'])
        if not are_valid:
            self.add_error('prereqs', "Prerequisites lead back to this course.")


class CoursesTable(tables.Table):
    major = ClassyColumn(css_class_base='major', accessor='major__abbreviation')
    catalog_number = ClassyColumn(verbose_name='Catalog Number', css_class_base='catnumber')
    title = ClassyColumn(css_class_base='coursetitle')
    credits_earned = ClassyColumn(css_class_base='credits')
    graduate = ClassyColumn(verbose_name="Course Level", css_class_base='courselevel')

    def render_graduate(self, value):
        if value is not None and value:
            show = "Graduate"
        else:
            show = "Undergrad"
        return show

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalog_number', 'graduate', 'title', 'credits_earned')
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'course_table'}


# when the major is known
class CoursesForMajorTable(tables.Table):
    catalog_number = ClassyColumn(verbose_name='Catalog Number', css_class_base='catnumber')
    title = ClassyColumn(css_class_base='coursetitle')
    credits_earned = ClassyColumn(css_class_base='credits')
    graduate = ClassyColumn(verbose_name="Course Level", css_class_base='courselevel')

    def render_graduate(self, value):
        if value is not None and value:
            show = "Graduate"
        else:
            show = "Undergrad"
        return show

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('catalog_number', 'graduate', 'title', 'credits_earned')
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'course_table'}


# for list of course with "met?" flag
class MajorCoursesMetTable(tables.Table):
    major = ClassyColumn(css_class_base='major', accessor='major__abbreviation')
    catalog_number = ClassyColumn(verbose_name='Catalog Number', css_class_base='catnumber')
    title = ClassyColumn(css_class_base='coursetitle')
    credits_earned = ClassyColumn(css_class_base='credits')
    met = ClassyBooleanColumn(css_class_base='met')
    letter_grade = ClassyColumn(verbose_name="Grade",
                                accessor='grade',
                                css_class_base='lettergrade',
                                order_by=('grade'))

    def render_letter_grade(self, value):
        return SectionStudent.letter_grade_for(value)

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalog_number', 'title', 'credits_earned', 'letter_grade', 'met')
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'majorcourse_table'}
