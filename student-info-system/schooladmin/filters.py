from django.contrib.auth.models import User
from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Concat
from django_filters import (CharFilter, ChoiceFilter, DateTimeFromToRangeFilter, FilterSet,
                            ModelChoiceFilter, BooleanFilter, RangeFilter)

from sis.models import (Course, CoursePrerequisite, Major, Message, Professor, Section, Semester,
                        Student, SectionStudent, Profile, ReferenceItem, SectionReferenceItem)


class UserFilter(FilterSet):
    username = CharFilter(lookup_expr='icontains')
    name = CharFilter(field_name='name',
                      label='Name',
                      method='filter_has_name',
                      lookup_expr='icontains')
    access_role = ChoiceFilter(field_name='profile__role',
                               label='Access Role',
                               choices=Profile.ROLES)
    major = ModelChoiceFilter(
        queryset=Major.objects.order_by('abbreviation'),
        # provided because it needs one. Will be ignoring this.
        field_name='name',
        method='filter_has_major',
        label='Major')

    def filter_has_major(self, queryset, name, value):
        return queryset.filter(
            Q(profile__professor__major__abbreviation=value) |
            Q(profile__student__major__abbreviation=value))

    def filter_has_name(self, queryset, name, value):
        return queryset.annotate(fullname=Concat('first_name', Value(' '), 'last_name')).filter(
            fullname__icontains=value).distinct()

    is_active = ChoiceFilter(label='Enabled?', choices=((True, 'Enabled'), (False, 'Disabled')))

    # TODO - implement (BJM)
    # class_level = ChoiceFilter(field_name='student__class_level',
    #                            label='Class Level',
    #                            choices=Student.CLASSLEVELS,
    #                                     ),method='filter_class_level')
    # gpa = RangeFilter(field_name='student__gpa')
    #
    # def filter_class_level(self, queryset, name, value):
    #     return queryset.filter(
    #         Q(professor__major__abbreviation=value) | Q(student__major__abbreviation=value))

    class Meta:
        model = User
        fields = [
            'username',
            'name',
            'major',
            # 'gpa', 'class_level',
            'access_role',
            'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super(UserFilter, self).__init__(*args, **kwargs)
        self.filters['is_active'].extra.update({'empty_label': 'Enabled/Disabled'})
        self.filters['access_role'].extra.update({'empty_label': 'Any Role'})
        self.filters['major'].extra.update({'empty_label': 'Any Major/Dept'})


class StudentFilter(FilterSet):
    username = CharFilter(lookup_expr='icontains')
    name = CharFilter(field_name='name',
                      label='Name',
                      method='filter_has_name',
                      lookup_expr='icontains')
    major = ModelChoiceFilter(
        queryset=Major.objects.order_by('abbreviation'),
        # provided because it needs one. Will be ignoring this.
        field_name='name',
        method='filter_has_major',
        label='Major')

    def filter_has_major(self, queryset, name, value):
        return queryset.filter(
            Q(profile__professor__major__abbreviation=value) |
            Q(profile__student__major__abbreviation=value))

    def filter_has_name(self, queryset, name, value):
        return queryset.annotate(fullname=Concat('first_name', Value(' '), 'last_name')).filter(
            fullname__icontains=value).distinct()

    is_active = ChoiceFilter(label='Enabled?', choices=((True, 'Enabled'), (False, 'Disabled')))

    class Meta:
        model = User
        fields = [
            'username',
            'name',
            'major',
            # 'gpa', 'class_level',
            'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super(StudentFilter, self).__init__(*args, **kwargs)
        self.filters['is_active'].extra.update({'empty_label': 'Enabled/Disabled'})
        self.filters['major'].extra.update({'empty_label': 'Any Major/Dept'})


# this is useful for the ModelChoice version of professor
#    def __init__(self, *args, **kwargs):
#        super(MajorFilter, self).__init__(*args, **kwargs)
#        self.filters['professors'].extra.update(
#            {'empty_label': 'Has Professor'})


class MajorFilter(FilterSet):
    abbreviation = CharFilter(field_name='abbreviation', lookup_expr='icontains')
    title = CharFilter(field_name='title', label='Title contains', lookup_expr='icontains')
    description = CharFilter(field_name='description',
                             label='Description contains',
                             lookup_expr='icontains')
    # this version lets them type part of the profs name
    professors = CharFilter(field_name='professor__profile__user__last_name',
                            lookup_expr='icontains',
                            label='Has Professor Name')
    # this version lets them pick professors
    #    professors = ModelChoiceFilter(queryset=Professor.objects,
    #                                  method='filter_has_prof',
    #                                  label='Has Professor')
    #    def filter_has_prof(self, queryset, name, value):
    #        return queryset.annotate(profname=Concat('professor__user__first_name',Value(' '),
    #                                                 'professor__user__last_name')).filter(profname__icontains=value)

    requires = CharFilter(
        Course.objects,
        label='Requires Course',
        method='filter_requires_course',
        distinct=True,
    )

    def filter_requires_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat('courses_required__major__abbreviation', Value(
            '-'), 'courses_required__catalog_number', Value(
                ' '), 'courses_required__title')).filter(slug__icontains=value).distinct()

    class Meta:
        model = Major
        fields = ['abbreviation', 'title', 'description', 'professors', 'requires']

        def __init__(self, *args, **kwargs):
            super(MajorFilter, self).__init__(*args, **kwargs)
            self.filters['abbreviation'].extra.update({'empty_label': 'Any Major/Department...'})


class SemesterFilter(FilterSet):
    session = ChoiceFilter(label="Session", choices=Semester.SESSIONS, field_name='session')
    year = RangeFilter(field_name='year')

    class Meta:
        model = Semester
        fields = ['session', 'year']

    def __init__(self, *args, **kwargs):
        super(SemesterFilter, self).__init__(*args, **kwargs)
        self.filters['session'].extra.update({'empty_label': 'Session...'})


class SectionFilter(FilterSet):
    semester = CharFilter(Semester.objects, label='Semester', method='filter_semester')

    professor = CharFilter(label='Professor Name Contains', method='filter_professor')

    course_descr = CharFilter(Course.objects, label='Course Info', method='filter_course')

    hours = CharFilter(field_name='hours', lookup_expr='icontains')

    location = CharFilter(field_name='location', lookup_expr='icontains')

    status = ChoiceFilter(choices=Section.STATUSES, field_name='status')

    # seats_remaining = RangeFilter()

    def filter_semester(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'semester__session', Value('-'), 'semester__year', output_field=CharField())).filter(
                slug__icontains=value)

    def filter_professor(self, queryset, name, value):
        return queryset.annotate(slug=Concat('professor__profile__user__first_name',
                                             Value(' '),
                                             'professor__profile__user__last_name',
                                             output_field=CharField())).filter(
                                                 slug__icontains=value)

    def filter_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'course__major__abbreviation',
            Value('-'),
            'course__catalog_number',
            Value(' '),
            'course__title',
        )).filter(slug__icontains=value)

    def __init__(self, *args, **kwargs):
        super(SectionFilter, self).__init__(*args, **kwargs)
        self.filters['status'].extra.update({'empty_label': 'Any Status'})

    class Meta:
        model = Section
        fields = ['semester', 'course_descr', 'professor', 'hours', 'location', 'status']


class ItemFilter(FilterSet):
    course = CharFilter(Course.objects, label='Course Info', method='filter_course')

    def filter_course(self, queryset, name, value):
        return queryset.annotate(slug=Concat(
            'course__major__abbreviation',
            Value('-'),
            'course__catalog_number',
            Value(' '),
            'course__title',
        )).filter(slug__icontains=value)

    type = ChoiceFilter(choices=ReferenceItem.TYPES, field_name='type', label="Type")

    title = CharFilter(field_name='title', lookup_expr='icontains')
    description = CharFilter(field_name='description', lookup_expr='icontains')
    link = CharFilter(field_name='link', lookup_expr='icontains')

    def __init__(self, *args, **kwargs):
        super(ItemFilter, self).__init__(*args, **kwargs)
        self.filters['type'].extra.update({'empty_label': 'Any Type'})

    class Meta:
        model = ReferenceItem
        fields = ['course', 'type', 'title', 'description', 'link']
