from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup', views.signup, name='signup'),
    path('current_courses', views.current_courses, name='Current Courses'),
    path('departments', views.departments, name='Departments'),
    path('section_edit', views.section_edit, name='Edit a Section'),
]
