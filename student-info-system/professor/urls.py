from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

app_name = 'professor'

urlpatterns = [
    path('', views.index, name='index'),
    path('sections', views.sections, name='sections'),
]
