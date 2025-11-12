from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
    ]
    
    SUBJECT_CHOICES = [
        ('mathematics', 'Mathematics'),
        ('sciences', 'Sciences'),
        ('languages', 'Languages'),
        ('technology', 'Technology'),
        ('business', 'Business Studies'),
        ('arts', 'Arts & Humanities'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    subject_specialization = models.CharField(max_length=20, choices=SUBJECT_CHOICES, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"

    def clean(self):
        # Teachers should have subject specialization
        if self.role == 'teacher' and not self.subject_specialization:
            raise ValidationError('Teachers must have a subject specialization.')

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

# Safe signal handlers to prevent RelatedObjectDoesNotExist errors
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved - safely handle missing profiles"""
    try:
        # Try to get or create the profile
        profile, created = UserProfile.objects.get_or_create(user=instance)
        if not created:  # If it already existed, save it
            profile.save()
    except Exception as e:
        # If there's any error, create a new profile
        UserProfile.objects.create(user=instance)