from django.forms import ModelForm

from sis.models import AcademicProbationTask


class AcademicProbationTaskForm(ModelForm):
    class Meta:
        model = AcademicProbationTask
        fields = '__all__'
