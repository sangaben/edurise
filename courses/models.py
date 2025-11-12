from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='instructors/', blank=True, null=True)
    bio = models.TextField(blank=True)
    expertise = models.CharField(max_length=200, blank=True)
    
    @property
    def name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    modules_count = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(help_text="Duration in hours")
    is_popular = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    is_trending = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add this field for enrollment functionality
    enrolled_students = models.ManyToManyField(
        User,
        related_name='enrolled_courses',
        blank=True
    )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def progress(self):
        # This would typically be calculated based on user progress
        # For demo purposes, we'll return a random value
        import random
        return random.randint(10, 90)
    
    def __str__(self):
        return self.title
    
    def is_user_enrolled(self, user):
        """Check if a user is enrolled in this course"""
        if user.is_authenticated:
            return self.enrolled_students.filter(id=user.id).exists()
        return False