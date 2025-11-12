from django.urls import path
from . import views

urlpatterns = [
    path('', views.resources, name='resources'),
    path('upload/', views.upload, name='upload'),
]