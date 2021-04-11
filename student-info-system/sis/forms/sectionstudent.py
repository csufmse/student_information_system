from django import forms

from sis.models import (
    SectionStudent,)

from sis.forms.utils import *


class DropRequestForm(forms.Form):
    student_section = forms.ModelChoiceField(queryset=SectionStudent.objects.none())
    reason = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        fields = ('student_section', 'reason')

    def __init__(self, *args, **kwargs):
        sectionstudent_qs = kwargs.pop('sectionstudent_qs', None)
        super(DropRequestForm, self).__init__(*args, **kwargs)

        self.fields['student_section'].queryset = sectionstudent_qs
