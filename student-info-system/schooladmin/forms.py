from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, Student, UpperField, AccessRoles)


class UpperFormField(forms.CharField):

    def clean(self, value):
        supa_clean = super().clean(value)
        return str(supa_clean).upper()


class CourseChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return f'{obj.name}: {obj.title}'


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    role = forms.ChoiceField(choices=AccessRoles.ROLES, required=True, help_text='Select type of user')
    major = forms.ModelChoiceField(queryset=None, required=False)

    class Meta:
        model = User
        fields = ('role', 'username', 'first_name', 'last_name', 'email', 'password1',
                  'password2', 'major')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['major'].queryset = Major.objects.all()


class MajorCreationForm(forms.ModelForm):
    abbreviation = UpperFormField(max_length=6, help_text='Abbreviation')
    name = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Major
        fields = ('abbreviation', 'name', 'description')


class MajorEditForm(forms.ModelForm):
    name = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))
    courses_required = CourseChoiceField(queryset=Course.objects.all().order_by(
        'major', 'catalog_number'),
                                         widget=forms.CheckboxSelectMultiple,
                                         required=False)

    class Meta:
        model = Major
        fields = ('name', 'description', 'courses_required')


class CourseCreationForm(forms.ModelForm):
    major = forms.ModelChoiceField(queryset=Major.objects.all())
    catalog_number = forms.IntegerField(label='Number')
    title = forms.CharField(label='Title', max_length=256)
    description = forms.CharField(label_suffix='Description',
                                  max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))
    credits_earned = forms.DecimalField(label='Credits', max_digits=2, decimal_places=1)

    # prereqs = models.ManyToManyField('self', through='CoursePrerequisite')

    class Meta:
        model = Course
        fields = ('major', 'catalog_number', 'title', 'description', 'credits_earned')


class CourseEditForm(forms.ModelForm):
    major = forms.ModelChoiceField(queryset=Major.objects.all())

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

    # courses_required = CourseChoiceField(queryset=Course.objects.all(),
    #                                      widget=forms.CheckboxSelectMultiple,
    #                                      required=False)

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


class SemesterCreationForm(forms.Form):
    semester = forms.ChoiceField(choices=Semester.SEASONS)
    year = forms.IntegerField()
    date_started = forms.DateField()
    date_ended = forms.DateField()
    date_registration_opens = forms.DateField()
    date_last_drop = forms.DateField()

    class Meta:
        model = Semester
        fields = ('semester', 'year', 'date_started', 'date_ended', 'date_registration_opens',
                  'date_last_drop')


class UserEditForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    role = forms.ChoiceField(choices=AccessRoles.ROLES, required=True, help_text='Select type of user')
    major = forms.ModelChoiceField(queryset=Major.objects.all(), required=False)

    role.widget.attrs.update({'class': 'rolesel selectpicker'})
    major.widget.attrs.update({'class': 'majorsel selectpicker'})

    class Meta:
        model = User
        fields = ('role', 'first_name', 'last_name', 'email', 'major')


class SectionCreationForm(forms.ModelForm):
    semester = forms.ModelChoiceField(queryset=Semester.objects.filter(
        date_ended__gt=date.today()))
    course = forms.ModelChoiceField(queryset=Course.objects.all())
    number = forms.IntegerField()
    hours = forms.CharField(max_length=100)
    professor = forms.ModelChoiceField(queryset=Professor.objects.all())
    capacity = forms.IntegerField()

    class Meta:
        model = Section
        fields = ('semester', 'course', 'number', 'hours', 'professor', 'capacity')


class SectionEditForm(forms.ModelForm):
    hours = forms.CharField(max_length=100)
    professor = forms.ModelChoiceField(queryset=Professor.objects.none())
    capacity = forms.IntegerField()

    class Meta:
        model = Section
        fields = ('hours', 'professor', 'capacity')

    def __init__(self, *args, **kwargs):
        super(SectionEditForm, self).__init__(*args, **kwargs)

        # we defer loading of professors until we know what major is chosen
        if kwargs['instance']:
            major = kwargs['instance'].course.major
            if major:
                self.fields['professor'].queryset = Professor.objects.filter(user__is_active=True,
                                                                             major=major)
