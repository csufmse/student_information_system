from django_filters import (CharFilter, ChoiceFilter, FilterSet, ModelChoiceFilter, RangeFilter)

from sis.models import (SectionStudent, Section, Semester, Major)


class SectionStudentFilter(FilterSet):
    semester = CharFilter(label='Semester', method='filter_semester')

    def filter_semester(self, queryset, name, value):
        return queryset.annotate(slug=Concat('section__semester__session',
                                             Value('-'),
                                             'section__semester__year',
                                             output_field=CharField())).filter(
                                                 slug__icontains=value)

    sec_status = ChoiceFilter(choices=Section.STATUSES,
                              field_name='section__status',
                              label="Section Status")
    student_status = ChoiceFilter(choices=SectionStudent.STATUSES,
                                  field_name='status',
                                  label="Student Status")
    grade = ChoiceFilter(choices=SectionStudent.GRADES, field_name='grade', label="Grade")

    def __init__(self, *args, **kwargs):
        super(SectionStudentFilter, self).__init__(*args, **kwargs)
        self.filters['sec_status'].extra.update({'empty_label': 'Any Section Status'})
        self.filters['student_status'].extra.update({'empty_label': 'Any Student Status'})
        self.filters['grade'].extra.update({'empty_label': 'Any Grade'})

    class Meta:
        model = SectionStudent
        fields = ['semester', 'sec_status', 'student_status', 'grade']


class StudentHistoryFilter(FilterSet):
    semester = CharFilter(label='Semester', method='filter_semester')
    major = ModelChoiceFilter(queryset=Major.objects,
                              field_name='section__course__major',
                              label='Major')

    def filter_semester(self, queryset, name, value):
        return queryset.annotate(slug=Concat('section__semester__session',
                                             Value('-'),
                                             'section__semester__year',
                                             output_field=CharField())).filter(
                                                 slug__icontains=value)

    student_status = ChoiceFilter(choices=SectionStudent.STATUSES,
                                  field_name='status',
                                  label="Student Status")
    grade = ChoiceFilter(choices=SectionStudent.GRADES, field_name='grade', label="Grade")

    def __init__(self, *args, **kwargs):
        super(StudentHistoryFilter, self).__init__(*args, **kwargs)
        self.filters['student_status'].extra.update({'empty_label': 'Any Status'})
        self.filters['grade'].extra.update({'empty_label': 'Any Grade'})
        self.filters['major'].extra.update({'empty_label': 'Any Major'})

    class Meta:
        model = SectionStudent
        fields = ['semester', 'major', 'student_status', 'grade']
