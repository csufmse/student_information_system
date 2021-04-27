from django.urls import path
from django.shortcuts import redirect

from sis.views import messages, profile, users, majors, sectionreferenceitem, users

from . import views

app_name = 'sis'
urlpatterns = [
    path('', lambda request: redirect('/', permanent=True)),
    path('profile', profile.profile, name='profile'),
    path('profile/edit', profile.profile_edit, name='profile_edit'),
    path('access_denied', views.access_denied, name='access_denied'),
    path('majors', majors.majors, name='majors'),
    path('major/<int:majorid>', majors.major, name='major'),
    path('messages', messages.usermessages, name='messages'),
    path('message/<int:id>', messages.message, name='message'),
    path('user/<int:userid>/change_password', users.user_change_password, name='change_password'),
    path('secitem/<int:id>', sectionreferenceitem.sectionreferenceitem, name='secitem'),
]
