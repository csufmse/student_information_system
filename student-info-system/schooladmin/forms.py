from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from sis.models import ( Major, Semester, Course,
    UpperField, CharField, IntegerField, DateField)

ROLE_CHOICES = (
    ('Student', 'Student'),
    ('Professor', 'Professor'),
    ('Admin', 'Admin'),
)


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
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, help_text='Select type of user')
    major = forms.ModelChoiceField(queryset=None, required=False)

    class Meta:
        model = User
        fields = ('role', 'username', 'first_name', 'last_name', 'email', 'password1',
                  'password2', 'major')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # this may be necessary: applyClassConfig2FormControl(self)
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
    courses_required = CourseChoiceField(queryset=Course.objects.all(),
                                         widget=forms.CheckboxSelectMultiple,
                                         required=False)

    class Meta:
        model = Major
        fields = ('name', 'description', 'courses_required')




SEASON = (('FALL', 'Fall'), ('SPRING', 'Spring'), ('SUMMER', 'Summer'), ('WINTER', 'Winter'))

class SemesterCreationForm(forms.Form):
    semester = CharField(max_length=6, choices=SEASON, default='FA')
    year = IntegerField(default=2000)
    date_started = DateField(auto_now=False)
    date_ended = DateField(auto_now=False)
    date_registration_opens = DateField(auto_now=False)
    date_last_drop = DateField(auto_now=False)

    class Meta:
        model = Semester
        fields = ('semester', 'year', 'date_started', 'date_ended', 'date_registration_opens',
                  'date_last_drop')


class UserEditForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, help_text='Select type of user')
    major = forms.ModelChoiceField(queryset=Major.objects.all(), required=False)

    role.widget.attrs.update({'class': 'rolesel selectpicker'})
    major.widget.attrs.update({'class': 'majorsel selectpicker'})

    class Meta:
        model = User
        fields = ('role', 'first_name', 'last_name', 'email', 'major')
