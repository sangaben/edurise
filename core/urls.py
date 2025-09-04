# core/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Example home view
    path('upload/', views.upload, name='upload'), 
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('resources/', views.resources, name='resources'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
     path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('logout-confirm/', views.logout_confirm, name='logout_confirm'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
]
