from django_filters import (ChoiceFilter, FilterSet, RangeFilter)

from sis.models import (
    Semester,)


class SemesterFilter(FilterSet):
    session = ChoiceFilter(label="Session", choices=Semester.SESSIONS, field_name='session')
    year = RangeFilter(field_name='year')

    class Meta:
        model = Semester
        fields = ['session', 'year']

    def __init__(self, *args, **kwargs):
        super(SemesterFilter, self).__init__(*args, **kwargs)
        self.filters['session'].extra.update({'empty_label': 'Session...'})
