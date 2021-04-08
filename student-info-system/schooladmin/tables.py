import django_tables2 as tables
from django.contrib.auth.models import User

from sis.models import *
from sis.tables import *


class FullUsersTable(tables.Table):
    name = NameColumn(css_class_base='user_name')
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
        model = User
        fields = ('username', 'name', 'student_major', 'student_gpa', 'credits_earned',
                  'class_level', 'professor_department', 'access_role', 'is_active')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class StudentsTable(tables.Table):
    name = NameColumn(css_class_base='user_name')
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
        model = User
        fields = ('username', 'name', 'student_major', 'student_gpa', 'credits_earned',
                  'class_level', 'is_active')
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class StudentInMajorTable(tables.Table):
    name = NameColumn(css_class_base='user_name')
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
        model = User
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class MajorsTable(tables.Table):
    abbreviation = ClassyColumn(css_class_base='major')
    name = ClassyColumn(css_class_base='majorname')
    description = ClassyColumn(css_class_base='majordescr')

    class Meta:
        model = Major
        template_name = "django_tables2/bootstrap.html"
        fields = ('abbreviation', 'name', 'description')
        row_attrs = {'class': 'major_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'major_table'}


class UsersTable(tables.Table):
    name = NameColumn(css_class_base='user_name')
    username = ClassyColumn(css_class_base='username')

    class Meta:
        attrs = {"class": 'user_table'}
        fields = ('username', 'name')
        model = User
        row_attrs = {'class': 'user_row', 'data-id': lambda record: record.pk}
        template_name = "django_tables2/bootstrap.html"


class CoursesTable(tables.Table):
    major = ClassyColumn(css_class_base='major', accessor='major__abbreviation')
    catalog_number = ClassyColumn(verbose_name='Catalog Number', css_class_base='catnumber')
    title = ClassyColumn(css_class_base='coursetitle')
    credits_earned = ClassyColumn(css_class_base='credits')

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalog_number', 'title', 'credits_earned')
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'course_table'}


# when the major is known
class CoursesForMajorTable(tables.Table):
    catalog_number = ClassyColumn(verbose_name='Catalog Number', css_class_base='catnumber')
    title = ClassyColumn(css_class_base='coursetitle')
    credits_earned = ClassyColumn(css_class_base='credits')

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('catalog_number', 'title', 'credits_earned')
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'course_table'}


# for list of course with "met?" flag
class MajorCoursesMetTable(tables.Table):
    major = ClassyColumn(css_class_base='major', accessor='major__abbreviation')
    catalog_number = ClassyColumn(verbose_name='Catalog Number', css_class_base='catnumber')
    title = ClassyColumn(css_class_base='coursetitle')
    credits_earned = ClassyColumn(css_class_base='credits')
    met = ClassyBooleanColumn(css_class_base='met')

    class Meta:
        model = Course
        template_name = "django_tables2/bootstrap.html"
        fields = ('major', 'catalog_number', 'title', 'credits_earned', 'met')
        row_attrs = {'class': 'course_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'majorcourse_table'}


class SemestersTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='name',
                            order_by=('semester_order'))
    session = ClassyColumn(verbose_name='Session',
                           css_class_base='session',
                           accessor='session',
                           order_by=('session_order'))
    year = ClassyColumn(css_class_base='year')
    date_registration_opens = ClassyColumn(verbose_name='Registration Opens',
                                           css_class_base='date')
    date_registration_closes = ClassyColumn(verbose_name='Registration Closes',
                                            css_class_base='date')
    date_last_drop = ClassyColumn(verbose_name='Date of Last Drop', css_class_base='date')
    date_started = ClassyColumn(verbose_name='Start of Classes', css_class_base='date')
    date_ended = ClassyColumn(verbose_name='End of Classes', css_class_base='date')

    class Meta:
        model = Semester
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'session', 'year', 'date_registration_opens',
                  'date_registration_closes', 'date_started', 'date_last_drop', 'date_ended')
        attrs = {"class": 'semester_table'}
        row_attrs = {'class': 'semester_row', 'data-id': lambda record: record.pk}


class SemestersSummaryTable(tables.Table):
    year = ClassyColumn(verbose_name='Year', css_class_base='year')
    session = ClassyColumn(verbose_name='Semester',
                           css_class_base='session',
                           accessor='name',
                           order_by=('semester_order'))

    class Meta:
        model = Semester
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'year',
            'session',
        )
        attrs = {"class": 'semester_table'}
        row_attrs = {'class': 'semester_row', 'data-id': lambda record: record.pk}


class SectionsTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='semester',
                            order_by=('semester.semester_order'))
    course = ClassyColumn(css_class_base='course', accessor='course__name')
    number = ClassyColumn(css_class_base='section_number')
    status = ClassyColumn(css_class_base='sectionstatus')
    course_title = ClassyColumn(css_class_base='coursetitle')
    hours = ClassyColumn(css_class_base='hours')
    location = ClassyColumn(css_class_base='location')
    professor = ClassyColumn(css_class_base='user_name', accessor='professor__profile__name')
    capacity = ClassyColumn(css_class_base='capac')
    seats_remaining = ClassyColumn(css_class_base='remaining')

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'course', 'number', 'status', 'course_title', 'hours', 'location',
                  'professor', 'capacity', 'seats_remaining')
        row_attrs = {'class': 'section_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'section_table'}


# for when Class is known
class SectionForClassTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='semester__name',
                            order_by=('semester_order'))
    section = ClassyColumn(css_class_base='section_name', accessor='name')
    status = ClassyColumn(css_class_base='sectionstatus')
    hours = ClassyColumn(css_class_base='hours')
    location = ClassyColumn(css_class_base='location')
    professor = ClassyColumn(css_class_base='username', accessor='professor__profile__name')
    capacity = ClassyColumn(css_class_base='capac')
    seats_remaining = ClassyColumn(css_class_base='remaining')

    class Meta:
        model = Section
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'section', 'status', 'hours', 'location', 'professor', 'capacity',
                  'seats_remaining')
        row_attrs = {'class': 'section_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'section_table'}


# shows all info: semester, course, section, student
class SectionStudentsTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='name',
                            order_by=('semester_order'))
    course = ClassyColumn(accessor='course', css_class_base='course')
    username = ClassyColumn(accessor='student__profile__user__username',
                            css_class_base='username')
    name = ClassyColumn(accessor='student__profile__user__name', css_class_base='user_name')
    major = ClassyColumn(accessor='student__profile__major__abbreviation', css_class_base='major')
    sec_status = ClassyColumn(
        verbose_name="Section Status",
        css_class_base='sectionstatus',
        accessor='section__status',
    )
    stud_status = ClassyColumn(
        verbose_name="Student Status",
        css_class_base='sectionstudentstatus',
        accessor='status',
    )
    letter_grade = ClassyColumn(verbose_name="Grade",
                                accessor='grade',
                                css_class_base='lettergrade')

    class Meta:
        model = SectionStudent
        template_name = "django_tables2/bootstrap.html"
        fields = ('semester', 'course', 'username', 'name', 'major', 'sec_status', 'stud_status',
                  'letter_grade')
        row_attrs = {
            'class': 'sectionstudent_row',
            'data-id': lambda record: record.student.profile.user.pk
        }
        attrs = {"class": 'sectionstudent_table'}


# for when the class is known
class StudentInSectionTable(tables.Table):
    username = ClassyColumn(accessor='student__profile__user__username',
                            css_class_base='username')
    name = ClassyColumn(accessor='student__profile__user__name', css_class_base='user_name')
    major = ClassyColumn(accessor='student__major__abbreviation', css_class_base='major')
    gpa = ClassyColumn(accessor='student__gpa', css_class_base='gpa')

    def render_gpa(self, value):
        return '{:0.2f}'.format(value)

    status = ClassyColumn(
        verbose_name="Status",
        css_class_base='sectionstatus',
        accessor='status',
    )
    letter_grade = ClassyColumn(verbose_name="Grade",
                                accessor='grade',
                                css_class_base='lettergrade')

    class Meta:
        model = SectionStudent
        template_name = "django_tables2/bootstrap.html"
        fields = ('username', 'name', 'major', 'gpa', 'status', 'letter_grade')
        row_attrs = {
            'class': 'sectionstudent_row',
            'data-id': lambda record: record.student.profile.user.pk
        }
        attrs = {"class": 'sectionstudent_table'}


# for when the student is known
class StudentHistoryTable(tables.Table):
    semester = ClassyColumn(verbose_name='Semester',
                            css_class_base='semester',
                            accessor='section__semester__name')
    section = ClassyColumn(css_class_base='section_name', accessor='section__name')
    course_title = ClassyColumn(accessor='section__course__title', css_class_base='coursetitle')
    credits_earned = ClassyColumn(
        verbose_name='Credits',
        css_class_base='credits',
        accessor='section__course__credits_earned',
    )
    status = ClassyColumn(
        verbose_name="Status",
        css_class_base='sectionstatus',
        accessor='status',
    )
    letter_grade = ClassyColumn(verbose_name="Grade",
                                accessor='grade',
                                css_class_base='lettergrade')

    class Meta:
        model = SectionStudent
        fields = ('semester', 'section', 'course_title', 'credits_earned', 'status',
                  'letter_grade')
        template_name = "django_tables2/bootstrap.html"
        row_attrs = {
            'class': 'sectionstudent_row',
            'data-id': lambda record: record.student.profile.user.pk
        }
        attrs = {"class": 'sectionstudent_table'}


class ProfReferenceItemsTable(tables.Table):
    course = ClassyColumn(css_class_base='course', accessor='course__name')
    type = ClassyColumn(verbose_name='Type', css_class_base='item_type')
    title = ClassyColumn(css_class_base='item_title')
    link = tables.TemplateColumn(
        '{% if record.link %}<a href="{{record.link}}" target="_blank">' +
        '{{record.link}}</a>{% endif %}')
    edition = ClassyColumn(css_class_base='item_edition')
    description = ClassyColumn(css_class_base='item_description')

    class Meta:
        model = ReferenceItem
        template_name = "django_tables2/bootstrap.html"
        fields = ('course', 'type', 'title', 'edition', 'description', 'link')
        row_attrs = {'class': 'refitem_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'items_table'}


class SectionReferenceItemsTable(tables.Table):
    index = ClassyColumn(verbose_name="#", css_class_base='item_index')
    type = ClassyColumn(verbose_name='Type', css_class_base='item_type', accessor='item__type')
    title = ClassyColumn(css_class_base='item_title', accessor='item__title')
    link = tables.TemplateColumn(
        '{% if record.item.link %}<a href="{{record.item.link}}" target="_blank">' +
        '{{record.item.link}}</a>{% endif %}')
    edition = ClassyColumn(css_class_base='item_edition', accessor='item__edition')
    description = ClassyColumn(css_class_base='item_description', accessor='item__description')

    class Meta:
        model = SectionReferenceItem
        template_name = "django_tables2/bootstrap.html"
        fields = ('index', 'type', 'title', 'edition', 'description', 'link')
        row_attrs = {'class': 'secrefitem_row', 'data-id': lambda record: record.pk}
        attrs = {"class": 'secitems_table'}


class MessageTable(tables.Table):
    recipient = ClassyColumn(verbose_name="To", css_class_base='message_addr')
    sender = ClassyColumn(verbose_name="From", css_class_base='message_addr')
    time_read = ClassyDateTimeColumn(verbose_name="Read at",
                                     css_class_base='message_date',
                                     format='Y-m-d H:i')
    time_sent = ClassyDateTimeColumn(verbose_name="Sent at",
                                     css_class_base='message_date',
                                     format='Y-m-d H:i')
    subject = ClassyColumn(verbose_name="Subject", css_class_base='message_subject')
    high_priority = ClassyColumn(verbose_name="Priority", css_class_base='message_priority')

    def render_high_priority(self, value):
        if value is not None and value:
            show = "*"
        else:
            show = ""
        return show

    unread = ClassyColumn(verbose_name="New", accessor='unread', css_class_base='message_unread')

    def render_unread(self, value, record):
        if value:
            show = "*"
        else:
            show = ""
        return show

    class Meta:
        model = Message
        template_name = "django_tables2/bootstrap.html"
        fields = ('unread', 'high_priority', 'time_sent', 'recipient', 'sender', 'subject')
        row_attrs = {
            'class': (lambda record: 'message_row unread' if record.unread else 'message_row'),
            'data-id': lambda record: record.pk
        }
        attrs = {"class": 'message_table'}


def classes_for(record):
    cl = 'message_row'
    if record.unread:
        cl += ' unread'
    if record.time_archived is not None:
        cl += ' archived'

    return cl


class MessageReceivedTable(MessageTable):

    class Meta:
        exclude = ('recipient', 'time_read')
        row_attrs = {
            'class': (lambda record: classes_for(record)),
            'data-id': lambda record: record.pk
        }


class MessageSentTable(MessageTable):

    class Meta:
        exclude = ('sender', 'time_read')
        row_attrs = {
            'class': (lambda record: classes_for(record)),
            'data-id': lambda record: record.pk
        }
