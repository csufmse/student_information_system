from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from sis.models import Major, UpperField

ROLE_CHOICES = (
    ('Student', 'Student'),
    ('Professor', 'Professor'),
    ('Admin', 'Admin'),
)


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, help_text='Select type of user')
    major = forms.ModelChoiceField(queryset=None, required=False)

    class Meta:
        model = User
        fields = ('role', 'username', 'first_name', 'last_name', 'email', 'password1', 'password2',
                  'major')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # this may be necessary: applyClassConfig2FormControl(self)
        self.fields['major'].queryset = Major.objects.all()


class MajorCreationForm(forms.Form):
    abbreviation = UpperField(max_length=6, help_text='Abbreviation')
    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256,required=False)

    class Meta:
        model = Major
        fields = ('abbrevation','title','description')
