from django.urls import path, include

from . import views

urlpatterns = [
    path('current_schedule', views.current_schedule_view, name='current_schedule'),
]
