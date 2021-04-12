from django import forms


class UpperFormField(forms.CharField):

    def clean(self, value):
        supa_clean = super().clean(value)
        return str(supa_clean).upper()


class CourseChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return f'{obj.name}: {obj.title}'


class SectionStudentChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.section.name
