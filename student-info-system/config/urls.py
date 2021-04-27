import debug_toolbar
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from sis import views as sis_views

urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
    path('sis/', include('sis.urls')),
    path('student/', include('student.urls')),
    path("siteadmin/", admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('schooladmin/', include('schooladmin.urls')),
    path('professor/', include('professor.urls')),
    path('', sis_views.index),
]
