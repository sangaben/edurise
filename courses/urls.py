from django.urls import path
from . import views

urlpatterns = [
    path('', views.courses, name='courses'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
]