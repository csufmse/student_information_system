from django import forms
import django_tables2 as tables


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


# Each column and cell has its own CSS class based on the type of
# data in it.
def field_css_classes(field_name):
    return {'th': {'class': field_name + '_col'}, 'td': {'class': field_name + '_cell'}}


class ClassyColumn(tables.Column):

    def __init__(self, *args, **kwargs):
        if 'css_class_base' in kwargs:
            css_class_base = kwargs.pop('css_class_base', None)
            kwargs['attrs'] = field_css_classes(css_class_base)
        super(ClassyColumn, self).__init__(*args, **kwargs)


class ClassyBooleanColumn(tables.BooleanColumn):

    def __init__(self, *args, **kwargs):
        if 'css_class_base' in kwargs:
            css_class_base = kwargs.pop('css_class_base', None)
            kwargs['attrs'] = field_css_classes(css_class_base)
        super(ClassyBooleanColumn, self).__init__(*args, **kwargs)


class ClassyDateTimeColumn(tables.DateTimeColumn):

    def __init__(self, *args, **kwargs):
        if 'css_class_base' in kwargs:
            css_class_base = kwargs.pop('css_class_base', None)
            kwargs['attrs'] = field_css_classes(css_class_base)
        super(ClassyDateTimeColumn, self).__init__(*args, **kwargs)


class AbilityColumn(tables.BooleanColumn):
    header = "Enabled?"
