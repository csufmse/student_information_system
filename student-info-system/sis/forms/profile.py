from django import forms

from sis.models import (Profile)
from sis.forms.utils import *


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


class UnprivProfileEditForm(forms.ModelForm):
    bio = forms.CharField(max_length=256,
                          required=False,
                          widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Profile
        fields = ('bio',)


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
