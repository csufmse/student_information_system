from django.urls import include, path

from student import views

app_name = 'student'
urlpatterns = [
    path('', views.index, name='index'),
    path('course/<int:courseid>', views.course, name='course'),
    path('current_schedule', views.current_schedule_view, name='current_schedule'),
    path('drop/<int:id>', views.drop, name='drop'),
    path('history', views.history, name='history'),
    path('registration', views.registration_view, name='registration'),
    path('request_major_change', views.request_major_change, name='request_major_change'),
    path('secitem/<int:id>', views.secitem, name='secitem'),
    path('secitems', views.secitems, name='secitems'),
    path('section/<int:sectionid>', views.section, name='section'),
    path('sectionstudent/<int:id>', views.sectionstudent, name='sectionstudent'),
    path('semester/<int:semester_id>', views.semester, name='semester'),
    path('test_major', views.test_majors, name='test_majors'),
    path('user/<int:userid>', views.user, name='user'),
]
