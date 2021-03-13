from django.contrib import admin
from django.urls import path, include  # new
from sis import views as sis_views

urlpatterns = [
    path('sis/', include('sis.urls')),
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # new
    path('', sis_views.index),
]
