from django import forms

from sis.models import (Student, Major)
from sis.forms.utils import *


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
