from django_filters import CharFilter, FilterSet
from django.db.models import CharField, Value
from django.db.models.functions import Concat

from sis.models import Semester


class SemesterFilter(FilterSet):
    semester = CharFilter(Semester.objects, label='Semester', method='filter_semester')

    def filter_semester(self, queryset, name, value):
        return queryset.annotate(
            slug=Concat('session', Value('-'), 'year', output_field=CharField())).filter(
                slug__icontains=value)

    class Meta:
        model = Semester
        fields = ['semester']
