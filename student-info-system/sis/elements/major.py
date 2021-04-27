from django import forms
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django_filters import (
    CharFilter,
    FilterSet,
)
import django_tables2 as tables

from sis.models import Major, Profile, Course
from sis.elements.utils import *


class MajorFilter(FilterSet):
    abbreviation = CharFilter(field_name='abbreviation', lookup_expr='icontains')
    title = CharFilter(field_name='title', label='Title contains', lookup_expr='icontains')
    description = CharFilter(field_name='description',
                             label='Description contains',
                             lookup_expr='icontains')
    # this version lets them type part of the profs name
    professors = CharFilter(field_name='professor__profile__user__last_name',
                            lookup_expr='icontains',
                            label='Has Professor Name')
    # this version lets them pick professors
    #    professors = ModelChoiceFilter(queryset=Professor.objects,
    #                                  method='filter_has_prof',
    #                                  label='Has Professor')
    #    def filter_has_prof(self, queryset, name, value):
    #        return queryset.annotate(profname=Concat('professor__user__first_name',Value(' '),
    #                                                 'professor__user__last_name')).filter(profname__icontains=value)

    requires = CharFilter(
        Course.objects,
        label='Requires Course',
        method='filter_requires_course',
        distinct=True,
    )

    def filter_requires_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat('courses_required__major__abbreviation', Value(
            '-'), 'courses_required__catalog_number', Value(
                ' '), 'courses_required__title')).filter(slug__icontains=value).distinct()

    class Meta:
        model = Major
        fields = ['abbreviation', 'title', 'description', 'professors', 'requires']

        def __init__(self, *args, **kwargs):
            super(MajorFilter, self).__init__(*args, **kwargs)
            self.filters['abbreviation'].extra.update({'empty_label': 'Any Major/Department...'})


class MajorCreationForm(forms.ModelForm):
    abbreviation = UpperFormField(max_length=6, help_text='Abbreviation')
    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))
    contact = forms.ModelChoiceField(queryset=Profile.staff())

    class Meta:
        model = Major
        fields = ('abbreviation', 'title', 'description', 'contact')


class MajorEditForm(forms.ModelForm):
    abbreviation = UpperFormField(max_length=6, help_text='Abbreviation')
    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))
    contact = forms.ModelChoiceField(queryset=Profile.staff())
    courses_required = CourseChoiceField(queryset=Course.objects.all().order_by(
        'major', 'catalog_number'),
                                         widget=forms.CheckboxSelectMultiple,
                                         required=False)

    class Meta:
        model = Major
        fields = ('abbreviation', 'title', 'description', 'contact', 'courses_required')

    def __init__(self, *args, **kwargs):
        super(MajorEditForm, self).__init__(*args, **kwargs)
        # we defer loading of professors until we know what major is chosen
        if kwargs['instance']:
            the_major = kwargs['instance']
            if the_major:
                self.fields['contact'].queryset = Profile.objects.filter(
                    Q(role=Profile.ACCESS_ADMIN) |
                    (Q(role=Profile.ACCESS_PROFESSOR) & Q(professor__major=the_major)))


class MajorSelectForm(forms.Form):
    major = forms.ModelChoiceField(queryset=Major.objects.all())

    class Meta:
        fields = ('major')


class MajorChangeForm(forms.Form):
    major = forms.ModelChoiceField(queryset=Major.objects.all())
    reason = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        fields = ('major', 'reason')


class MajorsTable(tables.Table):
    abbreviation = ClassyColumn(css_class_base='major')
    name = ClassyColumn(css_class_base='majorname')
    description = ClassyColumn(css_class_base='majordescr')
    contact = ClassyColumn(css_class_base='username')

    class Meta:
        model = Major
        template_name = "django_tables2/bootstrap.html"
        fields = ('abbreviation', 'name', 'description', 'contact')
        row_attrs = {'class': 'major_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'major_table'}
