from django.urls import include, path

from . import views

app_name = 'student'
urlpatterns = [
    path('', views.index, name='index'),
    path('current_schedule', views.current_schedule_view, name='current_schedule'),
    path('registration', views.registration_view, name='registration'),
    path('profile/edit', views.profile_edit, name='profile_edit'),
    path('profile', views.profile, name='profile'),
    path('change_password', views.change_password, name='change_password'),
    path('course/<int:courseid>', views.course, name='course'),
    path('sectionstudent/<int:id>', views.sectionstudent, name='sectionstudent'),
    path('semester/<int:semester_id>', views.semester, name='semester'),
    path('major/<int:majorid>', views.major, name='major'),
]
