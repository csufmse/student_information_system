from django import forms

from sis.models import (ReferenceItem, Course)
from sis.forms.utils import *


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
