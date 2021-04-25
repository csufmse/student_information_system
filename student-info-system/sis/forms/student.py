from django import forms

from sis.models import (Student, Major)
from sis.forms.utils import *


class StudentCreationForm(forms.ModelForm):
    prefix = 's'
    major = forms.ModelChoiceField(queryset=None, required=False)
    grad_student = forms.ChoiceField(label="Student Type", choices=Student.STUDENT_TYPES)

    def __init__(self, *args, **kwargs):
        super(StudentCreationForm, self).__init__(*args, **kwargs)
        major = self.fields['major']
        major.widget.attrs.update({'class': 'major_sel selectpicker'})
        major.queryset = Major.objects.all()

    class Meta:
        model = Student
        fields = ('major', 'grad_student')


class StudentEditForm(forms.ModelForm):
    prefix = 's'
    major = forms.ModelChoiceField(queryset=Major.objects.all(), required=False)
    grad_student = forms.ChoiceField(label="Student Type", choices=Student.STUDENT_TYPES)

    class Meta:
        model = Student
        fields = ('major', 'grad_student')

    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)
        major = self.fields['major']
        major.widget.attrs.update({'class': 'major_sel selectpicker'})
