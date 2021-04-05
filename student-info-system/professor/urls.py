from django.urls import path

from . import views

app_name = 'professor'

urlpatterns = [
    path('', views.index, name='index'),
    path('sections', views.sections, name='sections'),
    path('section/<int:sectionid>/students',
         views.students_in_section,
         name='students_in_section'),
]
