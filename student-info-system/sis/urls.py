from django.urls import path
from sis.views import messages

from . import views

app_name = 'sis'
urlpatterns = [
    path('', views.index, name='index'),
    path('access_denied', views.access_denied, name='access_denied'),
    path('messages', messages.usermessages, name='messages'),
    path('message/<int:id>', messages.message, name='message'),
]
