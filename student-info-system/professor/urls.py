from django.urls import path

from . import views

app_name = 'professor'

urlpatterns = [
    path('', views.index, name='index'),
    path('sections', views.sections, name='sections'),
    path('sections/<int:sectionid>/section', views.section, name='section'),
    path('section/<int:studentid>/student', views.student, name='student'),
    path('section/<int:sectionid>/add-reference', views.add_reference, name='add_reference'),
]
