from django.urls import path, include

from . import views

app_name = 'schooladmin'
urlpatterns = [
    path('', views.index, name='index'),
    path('users', views.users, name='users'),
    path('user/<int:userid>', views.user, name='user'),
    path('new_user', views.new_user, name='new_user'),
]
