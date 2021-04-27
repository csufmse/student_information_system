from django.urls import path
from django.shortcuts import redirect

from student import views

app_name = 'student'

urlpatterns = [
    path('', lambda request: redirect('/', permanent=True)),
    path('current_schedule', views.current_schedule_view, name='current_schedule'),
    path('drop/<int:id>', views.drop, name='drop'),
    path('history', views.history, name='history'),
    path('secitems', views.secitems, name='secitems'),
    path('registration', views.registration_view, name='registration'),
    path('request_major_change', views.request_major_change, name='request_major_change'),
    path('request_transcript', views.request_transcript, name='request_transcript'),
    path('test_major', views.test_majors, name='test_majors'),
]
