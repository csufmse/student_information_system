from django.urls import include, path

from . import views

app_name = 'schooladmin'
urlpatterns = [
    path('', views.index, name='index'),
    path('users', views.users, name='users'),
    path('user/<int:userid>/change_password', views.user_change_password, name='change_password'),
    path('user/<int:userid>/edit', views.user_edit, name='user_edit'),
    path('user/<int:userid>', views.user, name='user'),
    path('user_new', views.user_new, name='user_new'),
    path('majors', views.majors, name='majors'),
    path('major/<str:abbreviation>/edit', views.major_edit, name='major_edit'),
    path('major/<str:abbreviation>', views.major, name='major'),
    path('major_new', views.major_new, name='major_new'),
    path('courses', views.courses, name='courses'),
    path('course/<int:courseid>/edit', views.course_edit, name='course_edit'),
    path('course/<int:courseid>/section_new', views.course_section_new,
         name='course_section_new'),
    path('course/<int:courseid>', views.course, name='course'),
    path('course_new', views.course_new, name='course_new'),
    path('sections', views.sections, name='sections'),
    path('section/<int:sectionid>/edit', views.section_edit, name='section_edit'),
    path('section/<int:sectionid>/students_manage',
         views.section_students_manage,
         name='section_students_manage'),
    path('section/<int:sectionid>', views.section, name='section'),
    path('section_new', views.section_new, name='section_new'),
    path('sectionstudent/<int:id>', views.sectionstudent, name='sectionstudent'),
    path('semesters', views.semesters, name='semesters'),
    path('semester_new', views.semester_new, name='semester_new'),
    path('semester/<int:semester_id>/section_new',
         views.semester_section_new,
         name='semester_section_new'),
    path('semester/<int:semester_id>/edit', views.semester_edit, name='semester_edit'),
    path('semester/<int:semester_id>', views.semester, name='semester'),
]
