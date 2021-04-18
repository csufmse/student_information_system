from django.forms import ModelForm

from sis.models import AcademicProbationTask, Interval


class AcademicProbationTaskForm(ModelForm):
    class Meta:
        model = AcademicProbationTask
        fields = ['title', 'description', 'frequency_type', 'date', 'active']
        field_order = ['title', 'description', 'frequency_type', 'date', 'active']


class IntervalForm(ModelForm):
    class Meta:
        model = Interval
        fields ='__all__'
        field_order = ['interval_type', 'interval_amount']
