from django.urls import path
from sis.views import messages, profile, users, majors

from . import views

app_name = 'sis'
urlpatterns = [
    path('', views.index, name='index'),
    path('profile', profile.profile, name='profile'),
    path('profile/edit', profile.profile_edit, name='profile_edit'),
    path('access_denied', views.access_denied, name='access_denied'),
    path('majors', majors.majors, name='majors'),
    path('major/<int:majorid>', majors.major, name='major'),
    path('messages', messages.usermessages, name='messages'),
    path('message/<int:id>', messages.message, name='message'),
    path('user/<int:userid>/change_password', users.user_change_password,
         name='change_password'),
]
