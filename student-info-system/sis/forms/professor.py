from django import forms

from sis.models import (Major, Professor)

from sis.forms.utils import *


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
