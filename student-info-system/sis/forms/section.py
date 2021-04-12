from datetime import date
from django import forms

from sis.models import (
    Course,
    CoursePrerequisite,
    Major,
    Professor,
    Section,
    SectionStudent,
    Profile,
    Semester,
    UpperField,
)

from sis.forms.utils import *


class SectionCreationForm(forms.ModelForm):
    semester = forms.ModelChoiceField(queryset=Semester.objects.filter(
        date_ended__gt=date.today()))
    semester.widget.attrs.update({'class': 'semester_sel selectpicker'})

    course = forms.ModelChoiceField(queryset=Course.objects.all())
    course.widget.attrs.update({'class': 'course_sel selectpicker'})

    hours = forms.CharField(max_length=100)

    location = forms.CharField(max_length=256, widget=forms.Textarea(attrs={'rows': 3}))

    professor = forms.ModelChoiceField(queryset=Professor.objects.all())
    professor.widget.attrs.update({'class': 'user_sel selectpicker'})

    capacity = forms.IntegerField()
    status = forms.ChoiceField(choices=Section.STATUSES)

    class Meta:
        model = Section
        fields = ('semester', 'course', 'hours', 'professor', 'capacity', 'location', 'status')


class SectionEditForm(forms.ModelForm):
    hours = forms.CharField(max_length=100)

    location = forms.CharField(max_length=256, widget=forms.Textarea(attrs={'rows': 3}))

    professor = forms.ModelChoiceField(queryset=Professor.objects.none())
    professor.widget.attrs.update({'class': 'user_sel selectpicker'})

    capacity = forms.IntegerField()
    status = forms.ChoiceField(choices=Section.STATUSES)

    class Meta:
        model = Section
        fields = ('hours', 'professor', 'capacity', 'location', 'status')

    def __init__(self, *args, **kwargs):
        super(SectionEditForm, self).__init__(*args, **kwargs)

        # we defer loading of professors until we know what major is chosen
        if kwargs['instance']:
            major = kwargs['instance'].course.major
            if major:
                self.fields['professor'].queryset = Professor.objects.filter(
                    profile__user__is_active=True, major=major)
