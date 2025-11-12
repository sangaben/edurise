from django.contrib import admin
from .models import Category, Instructor, Course

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'expertise']
    search_fields = ['user__first_name', 'user__last_name', 'expertise']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'instructor', 'level', 'is_popular', 'is_new']
    list_filter = ['category', 'level', 'is_popular', 'is_new', 'is_trending']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}