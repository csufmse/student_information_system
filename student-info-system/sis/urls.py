from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

app_name = 'sis'
urlpatterns = [
    path('', views.index, name='index'),
    path('access_denied', views.access_denied, name='access_denied'),
]
