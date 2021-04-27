from django import forms
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django_filters import (CharFilter, ChoiceFilter, FilterSet, ModelChoiceFilter)
import django_tables2 as tables
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm

from sis.elements.utils import *

from sis.models import (
    Major,
    Message,
    Professor,
    Semester,
    Student,
    Profile,
    User,
)


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

    graduate = ChoiceFilter(field_name='profile__student__grad_student',
                            label='Grad Student?',
                            choices=((True, 'Grad Student'), (False, 'Undergrad')))

    class Meta:
        model = User
        fields = ['username', 'name', 'major', 'access_role', 'graduate', 'is_active']

    def __init__(self, *args, **kwargs):
        super(UserFilter, self).__init__(*args, **kwargs)
        self.filters['is_active'].extra.update({'empty_label': 'Enabled/Disabled'})
        self.filters['access_role'].extra.update({'empty_label': 'Any Role'})
        self.filters['major'].extra.update({'empty_label': 'Any Major/Dept'})
        self.filters['graduate'].extra.update({'empty_label': 'Grad/Undergrad'})


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
        return queryset.filter(profile__student__major__abbreviation=value)

    def filter_has_name(self, queryset, name, value):
        return queryset.annotate(fullname=Concat('first_name', Value(' '), 'last_name')).filter(
            fullname__icontains=value).distinct()

    is_active = ChoiceFilter(label='Enabled?', choices=((True, 'Enabled'), (False, 'Disabled')))

    graduate = ChoiceFilter(field_name='profile__student__grad_student',
                            label='Grad Student?',
                            choices=((True, 'Grad Student'), (False, 'Undergrad')))

    class Meta:
        model = User
        fields = ['username', 'name', 'major', 'graduate', 'is_active']

    def __init__(self, *args, **kwargs):
        super(StudentFilter, self).__init__(*args, **kwargs)
        self.filters['is_active'].extra.update({'empty_label': 'Enabled/Disabled'})
        self.filters['major'].extra.update({'empty_label': 'Any Major/Dept'})
        self.filters['graduate'].extra.update({'empty_label': 'Grad/Undergrad'})


class ProfessorFilter(FilterSet):
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
        return queryset.filter(profile__professor__major__abbreviation=value)

    def filter_has_name(self, queryset, name, value):
        return queryset.annotate(fullname=Concat('first_name', Value(' '), 'last_name')).filter(
            fullname__icontains=value).distinct()

    class Meta:
        model = User
        fields = [
            'username',
            'name',
            'major',
        ]

    def __init__(self, *args, **kwargs):
        super(ProfessorFilter, self).__init__(*args, **kwargs)
        self.filters['major'].extra.update({'empty_label': 'Any Major/Dept'})


class UserCreationForm(DjangoUserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class FullUsersTable(tables.Table):
    name = ClassyColumn(
        css_class_base='user_name',
        accessor='get_full_name',
        order_by=("last_name", "first_name"),
    )
    username = ClassyColumn(css_class_base='username')
    student_major = ClassyColumn(verbose_name='Student Major',
                                 css_class_base='major',
                                 accessor='profile__student__major__abbreviation')
    professor_department = ClassyColumn(verbose_name='Professor Dept',
                                        css_class_base='major',
                                        accessor='profile__professor__major__abbreviation')
    is_active = AbilityColumn(null=False, attrs=field_css_classes('active'))
    access_role = ClassyColumn(verbose_name='User Role',
                               accessor='profile__rolename',
                               css_class_base='role')
    class_level = ClassyColumn(verbose_name='Class',
                               css_class_base='classlevel',
                               accessor='profile__student__class_level')
    student_gpa = ClassyColumn(verbose_name='GPA',
                               accessor='profile__student__gpa',
                               css_class_base='gpa')

    def render_student_gpa(self, value):
        return '{:0.2f}'.format(value)

    credits_earned = ClassyColumn(
        verbose_name='Credits',
        css_class_base='credits',
        accessor='profile__student__credits_earned',
    )

    class Meta:
        attrs = {"class": 'fulluser_table'}
        fields = ('username', 'name', 'student_major', 'student_gpa', 'credits_earned',
                  'class_level', 'professor_department', 'access_role', 'is_active')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class UsersTable(FullUsersTable):
    name = ClassyColumn(
        css_class_base='user_name',
        accessor='get_full_name',
        order_by=("last_name", "first_name"),
    )
    username = ClassyColumn(css_class_base='username')

    class Meta:
        attrs = {"class": 'user_table'}
        exclude = ('student_major', 'student_gpa', 'credits_earned', 'class_level',
                   'professor_department', 'access_role', 'is_active')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class StudentsTable(tables.Table):
    name = ClassyColumn(
        css_class_base='user_name',
        accessor='get_full_name',
        order_by=("last_name", "first_name"),
    )
    username = ClassyColumn(css_class_base='username')
    student_major = ClassyColumn(verbose_name='Student Major',
                                 css_class_base='major',
                                 accessor='profile__student__major__abbreviation')
    is_active = AbilityColumn(null=False, attrs=field_css_classes('active'))
    class_level = ClassyColumn(verbose_name='Class',
                               css_class_base='classlevel',
                               accessor='profile__student__class_level')
    student_gpa = ClassyColumn(verbose_name='GPA',
                               css_class_base='gpa',
                               accessor='profile__student__gpa')

    def render_student_gpa(self, value):
        return '{:0.2f}'.format(value)

    credits_earned = ClassyColumn(
        verbose_name='Credits',
        css_class_base='credits',
        accessor='profile__student__credits_earned',
    )

    class Meta:
        attrs = {"class": 'students_table'}
        fields = ('username', 'name', 'student_major', 'student_gpa', 'credits_earned',
                  'class_level', 'is_active')
        row_attrs = {'class': 'student_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class StudentInMajorTable(tables.Table):
    name = ClassyColumn(
        css_class_base='user_name',
        accessor='get_full_name',
        order_by=("last_name", "first_name"),
    )
    username = ClassyColumn(css_class_base='username')
    is_active = AbilityColumn(null=False, attrs=field_css_classes('active'))
    class_level = ClassyColumn(verbose_name='Class',
                               css_class_base='classlevel',
                               accessor='profile__student__class_level')
    gpa = ClassyColumn(verbose_name='GPA', css_class_base='gpa', accessor='profile__student__gpa')

    def render_gpa(self, value):
        return '{:0.2f}'.format(value)

    credits_earned = ClassyColumn(
        verbose_name='Credits',
        css_class_base='credits',
        accessor='profile__student__credits_earned',
    )

    class Meta:
        attrs = {"class": 'studentmajor_table'}
        fields = ('username', 'name', 'gpa', 'credits_earned', 'class_level')
        row_attrs = {'class': 'student_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class ProfessorsTable(tables.Table):
    name = ClassyColumn(
        css_class_base='user_name',
        accessor='get_full_name',
        order_by=("last_name", "first_name"),
    )
    username = ClassyColumn(css_class_base='username')
    department = ClassyColumn(verbose_name='Department',
                              css_class_base='major',
                              accessor='profile__professor__major__abbreviation')
    department_name = ClassyColumn(verbose_name='Department Name',
                                   css_class_base='majorname',
                                   accessor='profile__professor__major__title')

    class Meta:
        attrs = {"class": 'professors_table'}
        fields = ('username', 'name', 'department', 'department_name')
        row_attrs = {'class': 'professor_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"
