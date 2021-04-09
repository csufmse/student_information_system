from datetime import date
from django import forms
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.models import User

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Profile, Semester, Student, UpperField, ReferenceItem, Profile)


class UpperFormField(forms.CharField):

    def clean(self, value):
        supa_clean = super().clean(value)
        return str(supa_clean).upper()


class CourseChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return f'{obj.name}: {obj.title}'


class MajorCreationForm(forms.ModelForm):
    abbreviation = UpperFormField(max_length=6, help_text='Abbreviation')
    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Major
        fields = ('abbreviation', 'title', 'description')


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


class UserCreationForm(DjangoUserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class ProfileCreationForm(forms.ModelForm):
    role = forms.ChoiceField(choices=Profile.ROLES,
                             required=True,
                             help_text='Select type of user')
    role.widget.attrs.update({'class': 'role_sel selectpicker'})

    bio = forms.CharField(max_length=256,
                          required=False,
                          widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Profile
        fields = ('role', 'bio')


class StudentCreationForm(forms.ModelForm):
    prefix = 's'
    major = forms.ModelChoiceField(queryset=None, required=False)

    def __init__(self, *args, **kwargs):
        super(StudentCreationForm, self).__init__(*args, **kwargs)
        major = self.fields['major']
        major.widget.attrs.update({'class': 'major_sel selectpicker'})
        major.queryset = Major.objects.all()

    class Meta:
        model = Student
        fields = ('major',)


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


class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    role = forms.ChoiceField(choices=Profile.ROLES,
                             required=True,
                             help_text='Select type of user')
    role.widget.attrs.update({'class': 'role_sel selectpicker'})
    bio = forms.CharField(max_length=256,
                          required=False,
                          widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Profile
        fields = ('role', 'bio')


class StudentEditForm(forms.ModelForm):
    prefix = 's'
    major = forms.ModelChoiceField(queryset=Major.objects.all(), required=False)

    class Meta:
        model = Student
        fields = ('major',)

    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)
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


class ReferenceItemCreationForm(forms.ModelForm):
    type = forms.ChoiceField(choices=ReferenceItem.TYPES)
    type.widget.attrs.update({'class': 'type_sel selectpicker'})

    course = forms.ModelChoiceField(queryset=Course.objects.all())
    course.widget.attrs.update({'class': 'course_sel selectpicker'})

    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256,
                                  widget=forms.Textarea(attrs={'rows': 3}),
                                  required=False)
    link = forms.CharField(max_length=256, required=False)
    edition = forms.CharField(max_length=256, required=False)

    class Meta:
        model = ReferenceItem
        fields = ('type', 'course', 'title', 'description', 'link', 'edition')

    def __init__(self, *args, **kwargs):
        super(ReferenceItemCreationForm, self).__init__(*args, **kwargs)

        # we defer loading of courses until we know what major is chosen
        if 'initial' in kwargs:
            major = kwargs['initial']['professor'].major
            if major:
                self.fields['course'].queryset = Course.objects.filter(major=major)
        elif 'instance' in kwargs:
            major = kwargs['instance'].professor.major
            if major:
                self.fields['course'].queryset = Course.objects.filter(major=major)


class DemographicForm(forms.ModelForm):

    demo_age = forms.ChoiceField(label='Age Group', choices=Profile.AGE)
    demo_age.widget.attrs.update({'class': 'type_sel selectpicker'})
    demo_race = forms.ChoiceField(label='Race Group', choices=Profile.RACE)
    demo_race.widget.attrs.update({'class': 'type_sel selectpicker'})
    demo_gender = forms.ChoiceField(label='Gender', choices=Profile.GENDER)
    demo_gender.widget.attrs.update({'class': 'type_sel selectpicker'})
    demo_employment = forms.ChoiceField(label='Employment Status', choices=Profile.WORK_STATUS)
    demo_employment.widget.attrs.update({'class': 'type_sel selectpicker'})
    demo_income = forms.ChoiceField(label='Annual Household Income Segment',
                                    choices=Profile.ANNUAL_HOUSEHOLD_INCOME,
                                    help_text="Including respondent.")
    demo_income.widget.attrs.update({'class': 'type_sel selectpicker'})
    demo_education = forms.ChoiceField(label='Highest Education in Family',
                                       choices=Profile.HIGHEST_FAMILY_EDUCATION,
                                       help_text='Excluding respondent.')
    demo_education.widget.attrs.update({'class': 'type_sel selectpicker'})
    demo_orientation = forms.ChoiceField(label='Sexual Orienatation', choices=Profile.ORIENTATION)
    demo_orientation.widget.attrs.update({'class': 'type_sel selectpicker'})
    demo_marital = forms.ChoiceField(label='Marital Status', choices=Profile.MARITAL_STATUS)
    demo_marital.widget.attrs.update({'class': 'type_sel selectpicker'})
    demo_disability = forms.ChoiceField(label='Disability Group', choices=Profile.DISABILITY)
    demo_disability.widget.attrs.update({'class': 'type_sel selectpicker'})
    demo_veteran = forms.ChoiceField(label='Veteran Status', choices=Profile.VETERAN_STATUS)
    demo_veteran.widget.attrs.update({'class': 'type_sel selectpicker'})
    demo_citizenship = forms.ChoiceField(label='Citizenship', choices=Profile.CITIZENSHIP)
    demo_citizenship.widget.attrs.update({'class': 'type_sel selectpicker'})

    class Meta:
        model = Profile
        fields = ('demo_age', 'demo_race', 'demo_gender', 'demo_employment', 'demo_income',
                  'demo_education', 'demo_orientation', 'demo_marital', 'demo_disability',
                  'demo_veteran', 'demo_citizenship')
