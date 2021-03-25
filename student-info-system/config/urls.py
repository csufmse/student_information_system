from django.contrib import admin
from django.urls import include, path

from sis import views as sis_views

urlpatterns = [
    path('sis/', include('sis.urls')),
    path('student/', include('student.urls')),
    path("siteadmin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('schooladmin/', include('schooladmin.urls')),
    path('professor/', include('professor.urls')),
    path('', sis_views.index),
]
