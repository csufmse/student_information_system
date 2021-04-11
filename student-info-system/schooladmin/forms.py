from datetime import date
from django import forms
from django.db.models import Q

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Profile, Semester, UpperField, ReferenceItem)

from sis.forms.utils import *


class CourseCreationForm(forms.ModelForm):
    major = forms.ModelChoiceField(queryset=Major.objects.all())
    major.widget.attrs.update({'class': 'major_sel selectpicker'})

    catalog_number = forms.IntegerField(label='Number')
    title = forms.CharField(label='Title', max_length=256)
    description = forms.CharField(max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))
    credits_earned = forms.DecimalField(label='Credits', max_digits=2, decimal_places=1)

    # prereqs = models.ManyToManyField('self', through='CoursePrerequisite')

    class Meta:
        model = Course
        fields = ('major', 'catalog_number', 'title', 'description', 'credits_earned')


class CourseEditForm(forms.ModelForm):
    major = forms.ModelChoiceField(queryset=Major.objects.all())
    major.widget.attrs.update({'class': 'major_sel selectpicker'})

    catalog_number = forms.IntegerField(label='Number')
    title = forms.CharField(label='Title', max_length=256)
    description = forms.CharField(label='Description',
                                  max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))
    credits_earned = forms.DecimalField(label='Credits', max_digits=2, decimal_places=1)

    prereqs = CourseChoiceField(queryset=Course.objects.all(),
                                widget=forms.CheckboxSelectMultiple,
                                required=False)

    class Meta:
        model = Course
        fields = ('major', 'catalog_number', 'title', 'description', 'credits_earned', 'prereqs')

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


class SemesterCreationForm(forms.ModelForm):
    session = forms.ChoiceField(choices=Semester.SESSIONS)
    session.widget.attrs.update({'class': 'session_sel selectpicker'})
    year = forms.IntegerField()
    date_registration_opens = forms.DateField()
    date_registration_closes = forms.DateField()
    date_started = forms.DateField()
    date_ended = forms.DateField()
    date_last_drop = forms.DateField()

    def clean(self):
        rego = self.cleaned_data.get('date_registration_opens')
        regc = self.cleaned_data.get('date_registration_closes')
        st = self.cleaned_data.get('date_started')
        de = self.cleaned_data.get('date_ended')
        ld = self.cleaned_data.get('date_last_drop')
        if not (rego <= st <= ld <= de and rego <= regc <= de):
            raise forms.ValidationError('Dates are not in order.')

    class Meta:
        model = Semester
        fields = ('session', 'year', 'date_registration_opens', 'date_registration_closes',
                  'date_started', 'date_last_drop', 'date_ended')


class SemesterEditForm(forms.ModelForm):
    date_started = forms.DateField()
    date_ended = forms.DateField()
    date_registration_opens = forms.DateField()
    date_registration_closes = forms.DateField()
    date_last_drop = forms.DateField()

    def clean(self):
        rego = self.cleaned_data.get('date_registration_opens')
        regc = self.cleaned_data.get('date_registration_closes')
        st = self.cleaned_data.get('date_started')
        de = self.cleaned_data.get('date_ended')
        ld = self.cleaned_data.get('date_last_drop')
        if not (rego <= st <= ld <= de and rego <= regc <= de):
            raise forms.ValidationError('Dates are not in order.')

    class Meta:
        model = Semester
        fields = ('date_registration_opens', 'date_registration_closes', 'date_started',
                  'date_last_drop', 'date_ended')


class ProfessorCreationForm(forms.ModelForm):
    prefix = 'r'
    major = forms.ModelChoiceField(queryset=Major.objects.all(), required=False)

    class Meta:
        model = Professor
        fields = ('major',)

    def __init__(self, *args, **kwargs):
        super(ProfessorCreationForm, self).__init__(*args, **kwargs)
        major = self.fields['major']
        major.widget.attrs.update({'class': 'major_sel selectpicker'})


class ProfessorEditForm(forms.ModelForm):
    prefix = 'r'
    major = forms.ModelChoiceField(queryset=Major.objects.all(), required=False)

    class Meta:
        model = Professor
        fields = ('major',)

    def __init__(self, *args, **kwargs):
        super(ProfessorEditForm, self).__init__(*args, **kwargs)
        major = self.fields['major']
        major.widget.attrs.update({'class': 'major_sel selectpicker'})
