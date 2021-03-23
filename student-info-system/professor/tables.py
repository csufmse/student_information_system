import django_tables2 as tables
from django.contrib.auth.models import User
from sis.models import *

# from sis.models import Major, Course, Professor


# For User names we want to show the full name ("first last") but sort by "last, first"
class NameColumn(tables.Column):

    def render(self, record):
        return record.name

    def order(self, queryset, is_descending):
        queryset = queryset.order_by(
            ("-" if is_descending else "") + "name_sort")
        return (queryset, True)


class AbilityColumn(tables.BooleanColumn):
    header = "Enabled?"


class UsersTable(tables.Table):
    username = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    name = NameColumn(attrs={'th': {'style': 'text-align: center;'}})
    student_major = tables.Column(verbose_name='Student Major',
                                  accessor='student__major__abbreviation',
                                  attrs={
                                      'th': {
                                          'style': 'text-align: center;'
                                      },
                                      'td': {
                                          'align': 'center',
                                          'width': '90px',
                                      }
                                  })
    professor_department = tables.Column(verbose_name='Professor Dept',
                                         accessor='professor__major__abbreviation',
                                         attrs={
                                             'th': {
                                                 'style': 'text-align: center;'
                                             },
                                             'td': {
                                                 'align': 'center',
                                                 'width': '90px',
                                             }
                                         })
    is_active = AbilityColumn(null=False,
                              attrs={
                                  'th': {
                                      'style': 'text-align: center;'
                                  },
                                  'td': {
                                      'align': 'center',
                                      'width': '80px',
                                  }
                              })
    access_role = tables.Column(verbose_name='User Role',
                                attrs={
                                    'th': {
                                        'style': 'text-align: center;'
                                    },
                                    'td': {
                                        'align': 'center',
                                        'width': '90px',
                                    }
                                })

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ("username", "name", 'student_major', 'professor_department', "access_role",
                  "is_active")
        row_attrs = {'class': 'urow', 'data-id': lambda record: record.pk}


class MajorsTable(tables.Table):
    abbreviation = tables.Column(attrs={
        'th': {
            'style': 'text-align: center;'
        },
        'td': {
            'align': 'center'
        }
    })
    name = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    description = tables.Column(attrs={'th': {'style': 'text-align: center;'}})

    class Meta:
        model = Major
        template_name = "django_tables2/bootstrap.html"
        fields = ('abbreviation', 'name', 'description')
        row_attrs = {'class': 'mrow', 'data-id': lambda record: record.pk}


class BasicProfsTable(tables.Table):
    name = NameColumn(
        attrs={'th': {'style': 'text-align: center;'}, 'td': {'width': '200px'}})
    username = tables.Column(attrs={
        'th': {
            'style': 'text-align: center;'
        },
        'td': {
            'align': 'center',
            'width': '100px'
        }
    })

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ('username', 'name')
        attrs = {"class": 'bprof'}
        row_attrs = {'class': 'prow', 'data-id': lambda record: record.pk}


class BasicCoursesTable(tables.Table):
    major = tables.Column(attrs={
        'th': {
            'style': 'text-align: center;'
        },
        'td': {
            'align': 'center',
            'width': '70px'
        }
    })
    catalogNumber = tables.Column(verbose_name='Number',
                                  attrs={
                                      'th': {
                                          'style': 'text-align: center;'
                                      },
                                      'td': {
                                          'align': 'center',
                                          'width': '60px'
                                      }
                                  })
    title = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    credits_earned = tables.Column(attrs={
        'th': {
            'style': 'text-align: center;'
        },
        'td': {
            'align': 'center',
            'width': '75px'
        }
    })

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalogNumber', 'title', 'credits_earned')
        attrs = {"class": 'bcourse'}
        row_attrs = {'class': 'crow', 'data-id': lambda record: record.pk}


class SemestersTable(tables.Table):
    semester = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    year = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    date_started = tables.Column(
        attrs={'th': {'style': 'text-align: center;'}})
    date_ended = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    date_registration_opens = tables.Column(
        attrs={'th': {'style': 'text-align: center;'}})
    date_last_drop = tables.Column(
        attrs={'th': {'style': 'text-align: center;'}})

    class Meta:
        model = Semester
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'year', 'date_started', 'date_ended', 'date_registration_opens',
                  'date_last_drop')

        row_attrs = {'class': 'urow', 'data-id': lambda record: record.pk}


class CoursesTable(tables.Table):
    major = tables.Column(attrs={
        'th': {
            'class': 'mcol',
            'style': 'text-align: center;'
        },
        'td': {
            'class': 'mcell'
        }
    })
    catalogNumber = tables.Column(
        attrs={'th': {'class': 'cncol'}, 'td': {'class': 'cncell'}})
    title = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    credits_earned = tables.Column(
        attrs={'th': {'style': 'text-align: center;'}})

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalogNumber', 'title', 'credits_earned')
        row_attrs = {'class': 'crow', 'data-id': lambda record: record.pk}


class SectionsTable(tables.Table):
    semester = tables.Column(
        attrs={'th': {'class': 'cscol'}, 'td': {'class': 'cscell'}})
    course_descr = tables.Column(
        attrs={'th': {'class': 'cncol'}, 'td': {'class': 'cncell'}})
    number = tables.Column(
        attrs={'th': {'class': 'cnncol'}, 'td': {'class': 'cnncell'}})
    professor = tables.Column(
        attrs={'th': {'class': 'cpcol'}, 'td': {'class': 'cpcell'}})
    hours = tables.Column(
        attrs={'th': {'class': 'chcol'}, 'td': {'class': 'chcell'}})
    capacity = tables.Column(
        attrs={'th': {'class': 'cccol'}, 'td': {'class': 'cccell'}})

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'course_descr', 'number',
                  'hours', 'professor', 'capacity')
        row_attrs = {'class': 'srow', 'data-id': lambda record: record.pk}


class SectionStudentsTable(tables.Table):
    username = tables.Column(accessor='user__username',
                             attrs={
                                 'th': {
                                     'class': 'sucol'
                                 },
                                 'td': {
                                     'class': 'sucell'
                                 }
                             })
    name = tables.Column(
        attrs={'th': {'class': 'sncol'}, 'td': {'class': 'sncell'}})
    major = tables.Column(
        attrs={'th': {'class': 'smcol'}, 'td': {'class': 'smcell'}})
    status = tables.Column(verbose_name="Status",
                           accessor='sectionstudent__status',
                           attrs={
                               'th': {
                                   'class': 'smcol'
                               },
                               'td': {
                                   'class': 'smcell'
                               }
                           })
    letter_grade = tables.Column(verbose_name="Grade",
                                 accessor='sectionstudent__letter_grade',
                                 attrs={
                                     'th': {
                                         'class': 'smcol'
                                     },
                                     'td': {
                                         'class': 'smcell'
                                     }
                                 })

    class Meta:
        model = Student
        template_name = "django_tables2/bootstrap.html"
        fields = ("username", "name", 'major', 'status', 'letter_grade')
        row_attrs = {'class': 'srow', 'data-id': lambda record: record.pk}
