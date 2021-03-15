from django import forms
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
        GENDER_CHOICES = (...)
        email = forms.EmailField(label='Email address', max_length=75)
        first_name = forms.CharField(label='First Name')
        last_name = forms.CharField(label='Last Name')
        gender = forms.ChoiceField(widget=RadioSelect, choices=GENDER_CHOICES)
        date_of_birth = forms.DateField(initial=datetime.date.today)

        class Meta:
            model = Members
            fields = ('username', 'email', 'first_name', 'last_name')