from django import forms

from sis.models import (Course, CoursePrerequisite, Major, Semester)

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
