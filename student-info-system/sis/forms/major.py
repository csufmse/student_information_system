from django import forms
from django.db.models import Q

from sis.models import Major, Profile, Course
from sis.forms.utils import *


class MajorCreationForm(forms.ModelForm):
    abbreviation = UpperFormField(max_length=6, help_text='Abbreviation')
    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))
    contact = forms.ModelChoiceField(queryset=Profile.staff())

    class Meta:
        model = Major
        fields = ('abbreviation', 'title', 'description', 'contact')


class MajorEditForm(forms.ModelForm):
    abbreviation = UpperFormField(max_length=6, help_text='Abbreviation')
    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256,
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 3}))
    contact = forms.ModelChoiceField(queryset=Profile.staff())
    courses_required = CourseChoiceField(queryset=Course.objects.all().order_by(
        'major', 'catalog_number'),
                                         widget=forms.CheckboxSelectMultiple,
                                         required=False)

    class Meta:
        model = Major
        fields = ('abbreviation', 'title', 'description', 'contact', 'courses_required')

    def __init__(self, *args, **kwargs):
        super(MajorEditForm, self).__init__(*args, **kwargs)
        # we defer loading of professors until we know what major is chosen
        if kwargs['instance']:
            the_major = kwargs['instance']
            if the_major:
                self.fields['contact'].queryset = Profile.objects.filter(
                    Q(role=Profile.ACCESS_ADMIN) |
                    (Q(role=Profile.ACCESS_PROFESSOR) & Q(professor__major=the_major)))


class MajorSelectForm(forms.Form):
    major = forms.ModelChoiceField(queryset=Major.objects.all())

    class Meta:
        fields = ('major')


class MajorChangeForm(forms.Form):
    major = forms.ModelChoiceField(queryset=Major.objects.all())
    reason = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        fields = ('major', 'reason')
