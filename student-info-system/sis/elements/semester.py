from django_filters import CharFilter, FilterSet
from django.db.models import CharField, Value
from django.db.models.functions import Concat

import django_tables2 as tables

from sis.models import Semester

from sis.elements.utils import *


class SemesterFilter(FilterSet):
    semester = CharFilter(Semester.objects, label='Semester', method='filter_semester')

    def filter_semester(self, queryset, name, value):
        return queryset.annotate(
            slug=Concat('session', Value('-'), 'year', output_field=CharField())).filter(
                slug__icontains=value)

    class Meta:
        model = Semester
        fields = ['semester']


class SemesterCreationForm(forms.ModelForm):
    session = forms.ChoiceField(choices=Semester.SESSIONS,
                                label="Semester Session",
                                help_text=Semester._meta.get_field('session').help_text)
    session.widget.attrs.update({'class': 'session_sel selectpicker'})
    year = forms.IntegerField(label="Semester School Year",
                              help_text=Semester._meta.get_field('year').help_text)
    date_started = forms.DateField(label="Classes Start",
                                   help_text=Semester._meta.get_field('date_started').help_text)
    date_ended = forms.DateField(label="Classes End",
                                 help_text=Semester._meta.get_field('date_ended').help_text)
    date_registration_opens = forms.DateField(
        label="Registration Opens",
        help_text=Semester._meta.get_field('date_registration_opens').help_text)
    date_registration_closes = forms.DateField(
        label="Registration Closes",
        help_text=Semester._meta.get_field('date_registration_closes').help_text)
    date_last_drop = forms.DateField(
        label="Last Drop", help_text=Semester._meta.get_field('date_last_drop').help_text)
    date_finalized = forms.DateField(
        label="Grades Finalized", help_text=Semester._meta.get_field('date_finalized').help_text)

    def clean(self):
        rego = self.cleaned_data.get('date_registration_opens')
        regc = self.cleaned_data.get('date_registration_closes')
        st = self.cleaned_data.get('date_started')
        de = self.cleaned_data.get('date_ended')
        ld = self.cleaned_data.get('date_last_drop')
        df = self.cleaned_data.get('date_finalized')
        if not (rego <= st <= ld <= de and rego <= regc <= de and de <= df):
            raise forms.ValidationError('Dates are not in order.')
        overlappers = Semester.objects.filter(date_started__lte=de, date_ended__gte=st)
        if overlappers.count():
            name = overlappers[0].name
            raise forms.ValidationError(f'Classes (Start-End) overlap with those of {name}')

    class Meta:
        model = Semester
        fields = ('session', 'year', 'date_registration_opens', 'date_registration_closes',
                  'date_started', 'date_last_drop', 'date_ended', 'date_finalized')


class SemesterEditForm(forms.ModelForm):
    date_registration_opens = forms.DateField(label="Registration Opens")
    date_registration_closes = forms.DateField(label="Registration Closes")
    date_started = forms.DateField(label="Classes Start")
    date_ended = forms.DateField(label="Classes End")
    date_last_drop = forms.DateField(label="Last Drop")
    date_finalized = forms.DateField(
        label="Grades Finalized", help_text=Semester._meta.get_field('date_finalized').help_text)
    date_started = forms.DateField(help_text=Semester._meta.get_field('date_started').help_text)
    date_ended = forms.DateField(help_text=Semester._meta.get_field('date_ended').help_text)
    date_registration_opens = forms.DateField(
        help_text=Semester._meta.get_field('date_registration_opens').help_text)
    date_registration_closes = forms.DateField(
        help_text=Semester._meta.get_field('date_registration_closes').help_text)
    date_last_drop = forms.DateField(
        help_text=Semester._meta.get_field('date_last_drop').help_text)
    date_finalized = forms.DateField(
        label="Grades Finalized", help_text=Semester._meta.get_field('date_finalized').help_text)

    def clean(self):
        rego = self.cleaned_data.get('date_registration_opens')
        regc = self.cleaned_data.get('date_registration_closes')
        st = self.cleaned_data.get('date_started')
        de = self.cleaned_data.get('date_ended')
        ld = self.cleaned_data.get('date_last_drop')
        df = self.cleaned_data.get('date_finalized')
        if not (rego <= st <= ld <= de and rego <= regc <= de and de <= df):
            raise forms.ValidationError('Dates are not in order.')
        overlappers = Semester.objects.exclude(id=self.instance.id).filter(date_started__lte=de,
                                                                           date_ended__gte=st)
        if overlappers.count():
            name = overlappers[0].name
            raise forms.ValidationError(f'Classes (Start-End) overlap with those of {name}')

    class Meta:
        model = Semester
        fields = ('date_registration_opens', 'date_registration_closes', 'date_started',
                  'date_last_drop', 'date_ended', 'date_finalized')


class SemestersTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='name',
                            order_by=('year', 'session_order'))
    session = ClassyColumn(verbose_name='Session',
                           css_class_base='session',
                           accessor='session',
                           order_by=('session_order',))
    year = ClassyColumn(css_class_base='year')
    date_registration_opens = ClassyColumn(verbose_name='Registration Opens',
                                           css_class_base='date')
    date_registration_closes = ClassyColumn(verbose_name='Registration Closes',
                                            css_class_base='date')
    date_last_drop = ClassyColumn(verbose_name='Date of Last Drop', css_class_base='date')
    date_started = ClassyColumn(verbose_name='Start of Classes', css_class_base='date')
    date_ended = ClassyColumn(verbose_name='End of Classes', css_class_base='date')
    date_finalized = ClassyColumn(verbose_name='Grades Finalized', css_class_base='date')

    class Meta:
        model = Semester
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'session', 'year', 'date_registration_opens',
                  'date_registration_closes', 'date_started', 'date_last_drop', 'date_ended',
                  'date_finalized')
        attrs = {"class": 'semester_table'}
        row_attrs = {'class': 'semester_row', 'data-id': lambda record: record.pk}


class SemestersSummaryTable(SemestersTable):

    class Meta:
        model = Semester
        template_name = "django_tables2/bootstrap.html"
        exclude = ('date_registration_opens', 'id', 'date_registration_closes', 'date_started',
                   'date_last_drop', 'date_ended', 'date_finalized')
        attrs = {"class": 'semester_table'}
        row_attrs = {'class': 'semester_row', 'data-id': lambda record: record.pk}
