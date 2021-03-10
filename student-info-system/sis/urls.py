from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup', views.signup, name='signup'),
    path('current-courses', views.current_courses, name='current_courses'),
    path('majors', views.majors, name='majors'),
    path('section-edit', views.section_edit, name='edit_section'),
]
