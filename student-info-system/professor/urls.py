from django.urls import path
from django.shortcuts import redirect

from . import views

app_name = 'professor'

urlpatterns = [
    path('', lambda request: redirect('/', permanent=True)),
    path('sections', views.sections, name='sections'),
    path('sections/<int:sectionid>/section', views.section, name='section'),
    path('section/<int:studentid>/student', views.student, name='student'),
    path('course/<int:sectionid>/add-reference', views.add_reference, name='add_reference'),
]
