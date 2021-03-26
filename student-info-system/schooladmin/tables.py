import django_tables2 as tables
from django.contrib.auth.models import User

from sis.models import *


# For User names we want to show the full name ("first last") but sort by "last, first"
class NameColumn(tables.Column):

    def render(self, record):
        return record.name

    def order(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "name_sort")
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
    class_level = tables.Column(verbose_name='Class',
                                accessor='student__class_level',
                                attrs={
                                    'th': {
                                        'style': 'text-align: center;'
                                    },
                                    'td': {
                                        'align': 'center',
                                        'width': '90px',
                                    }
                                })
    student_gpa = tables.Column(verbose_name='GPA',
                                accessor='student__gpa',
                                attrs={
                                    'th': {
                                        'style': 'text-align: center;'
                                    },
                                    'td': {
                                        'align': 'center',
                                        'width': '90px',
                                    }
                                })

    def render_student_gpa(self, value):
        return '{:0.2f}'.format(value)

    credits_earned = tables.Column(verbose_name='Credits',
                                   accessor='student__credits_earned',
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
        fields = ('username', 'name', 'student_major', 'student_gpa', 'credits_earned',
                  'class_level', 'professor_department', 'access_role', 'is_active')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}


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
    name = NameColumn(attrs={'th': {'style': 'text-align: center;'}, 'td': {'width': '200px'}})
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
        row_attrs = {'class': 'prof_row', 'data-id': lambda record: record.pk}


class BasicCoursesTable(tables.Table):
    major = tables.Column(attrs={'th': {'class': 'major_col'}, 'td': {'class': 'major_cell'}})
    catalog_number = tables.Column(attrs={
        'th': {
            'class': 'catnumber_col'
        },
        'td': {
            'class': 'catnumber_cell'
        }
    })
    title = tables.Column(attrs={'th': {'class': 'course_col'}, 'td': {'class': 'course_cell'}})
    credits_earned = tables.Column(attrs={
        'th': {
            'class': 'credits_col'
        },
        'td': {
            'class': 'credits_cell'
        }
    })

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalog_number', 'title', 'credits_earned')
        attrs = {"class": 'bcourse'}
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}


class SemestersTable(tables.Table):
    semester = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    year = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    date_started = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    date_ended = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    date_registration_opens = tables.Column(attrs={'th': {'style': 'text-align: center;'}})
    date_last_drop = tables.Column(attrs={'th': {'style': 'text-align: center;'}})

    class Meta:
        model = Semester
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'year', 'date_started', 'date_ended', 'date_registration_opens',
                  'date_last_drop')

        row_attrs = {'class': 'urow', 'data-id': lambda record: record.pk}


class CoursesTable(tables.Table):
    major = tables.Column(attrs={'th': {'class': 'major_col'}, 'td': {'class': 'major_cell'}})
    catalog_number = tables.Column(attrs={
        'th': {
            'class': 'catnumber_col'
        },
        'td': {
            'class': 'catnumber_cell'
        }
    })
    title = tables.Column(attrs={'th': {'class': 'course_col'}, 'td': {'class': 'course_cell'}})
    credits_earned = tables.Column(attrs={
        'th': {
            'class': 'credits_col'
        },
        'td': {
            'class': 'credits_cell'
        }
    })

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalog_number', 'title', 'credits_earned')
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}


class SectionsTable(tables.Table):
    semester = tables.Column(attrs={'th': {'class': 'sem_col'}, 'td': {'class': 'sem_cell'}})
    course = tables.Column(attrs={'th': {'class': 'course_col'}, 'td': {'class': 'course_cell'}})
    number = tables.Column(attrs={'th': {'class': 'secnum_col'}, 'td': {'class': 'secnum_cell'}})
    status = tables.Column(attrs={
        'th': {
            'class': 'sectionstatus_col'
        },
        'td': {
            'class': 'sectionstatus_cell'
        }
    })
    course_title = tables.Column(attrs={
        'th': {
            'class': 'coursetitle_col'
        },
        'td': {
            'class': 'coursetitle_cell'
        }
    })
    hours = tables.Column(attrs={'th': {'class': 'hours_col'}, 'td': {'class': 'hours_cell'}})
    professor = tables.Column(attrs={'th': {'class': 'prof_col'}, 'td': {'class': 'prof_cell'}})
    capacity = tables.Column(attrs={'th': {'class': 'capac_col'}, 'td': {'class': 'capac_cell'}})
    seats_remaining = tables.Column(attrs={
        'th': {
            'class': 'remaining_col'
        },
        'td': {
            'class': 'remaining_cell'
        }
    })

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'course', 'number', 'status', 'course_title', 'hours', 'professor',
                  'capacity', 'seats_remaining')
        row_attrs = {'class': 'section_row', 'data-id': lambda record: record.pk}


class SectionStudentsTable(tables.Table):
    username = tables.Column(accessor='student__user__username',
                             attrs={
                                 'th': {
                                     'class': 'username_col'
                                 },
                                 'td': {
                                     'class': 'username_cell'
                                 }
                             })
    name = tables.Column(accessor='student__user__name',
                         attrs={
                             'th': {
                                 'class': 'name_col'
                             },
                             'td': {
                                 'class': 'name_cell'
                             }
                         })
    major = tables.Column(accessor='student__major',
                          attrs={
                              'th': {
                                  'class': 'major_col'
                              },
                              'td': {
                                  'class': 'major_cell'
                              }
                          })
    status = tables.Column(verbose_name="Status",
                           accessor='status',
                           attrs={
                               'th': {
                                   'class': 'sectionstatus_col'
                               },
                               'td': {
                                   'class': 'sectionstatus_cell'
                               }
                           })
    letter_grade = tables.Column(verbose_name="Grade",
                                 accessor='grade',
                                 attrs={
                                     'th': {
                                         'class': 'lettergrade_col'
                                     },
                                     'td': {
                                         'class': 'lettergrade_cell'
                                     }
                                 })

    class Meta:
        model = SectionStudent
        template_name = "django_tables2/bootstrap.html"
        fields = ('username', 'name', 'major', 'status', 'letter_grade')
        row_attrs = {
            'class': 'sectionstudent_row',
            'data-id': lambda record: record.student.user.pk
        }
