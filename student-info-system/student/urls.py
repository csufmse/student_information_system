from django.urls import path, include

from . import views

app_name = 'student'
urlpatterns = [
    path('index', views.index, name='index'),
    path('current_schedule',
         views.current_schedule_view,
         name='current_schedule'),
]
