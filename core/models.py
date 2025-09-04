from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import os
import uuid

def content_file_path(instance, filename):
    """Generate file path for uploaded content"""
    ext = filename.split('.')[-1]
    unique_id = uuid.uuid4().hex[:8]  # Add unique identifier
    filename = f"{slugify(instance.title)}-{unique_id}.{ext}"
    return os.path.join('content', instance.content_type, filename)

class UploadedContent(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('audio', 'Audio'),
        ('image', 'Image'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    content_type = models.CharField(
        max_length=10, 
        choices=CONTENT_TYPE_CHOICES,
        default='pdf'
    )
    file = models.FileField(upload_to=content_file_path)
    cover_image = models.ImageField(
        upload_to='content/covers/',
        blank=True,
        null=True,
        help_text="Optional cover image for videos/audio"
    )
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='uploaded_content'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Learning Resource'
        verbose_name_plural = 'Learning Resources'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while UploadedContent.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_file_extension(self):
        return os.path.splitext(self.file.name)[1][1:].lower()

    def get_file_size(self):
        if self.file:
            return self.file.size
        return 0

    def increment_download_count(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])

    def increment_views_count(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

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



#ad model


class Ad(models.Model):
    AD_POSITION_CHOICES = [
        ('top', 'Top Banner'),
        ('mid_content', 'Middle Content'),
        ('sidebar', 'Sidebar'),
        ('sidebar_bottom', 'Sidebar Bottom'),
        ('bottom', 'Bottom Banner'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    target_url = models.URLField(blank=True)
    cta_text = models.CharField(max_length=50, default="Learn More")
    position = models.CharField(max_length=20, choices=AD_POSITION_CHOICES, default='top')
    is_active = models.BooleanField(default=True)
    show_timer = models.BooleanField(default=False, help_text="Show countdown timer on ad")
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Advertisement"
        verbose_name_plural = "Advertisements"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"
    
    def is_currently_active(self):
        if not self.is_active:
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
    
class UploadedContent(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('audio', 'Audio'),
        ('image', 'Image'),
        ('youtube', 'YouTube'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    content_type = models.CharField(
        max_length=10, 
        choices=CONTENT_TYPE_CHOICES,
        default='pdf'
    )
    file = models.FileField(upload_to=content_file_path, blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True, help_text="Add YouTube video link here")
    cover_image = models.ImageField(
        upload_to='content/covers/',
        blank=True,
        null=True,
        help_text="Optional cover image for videos/audio"
    )
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='uploaded_content'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Learning Resource'
        verbose_name_plural = 'Learning Resources'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while UploadedContent.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    @property
    def youtube_id(self):
        """Extract the YouTube video ID from the URL."""
        if self.content_type == 'youtube' and self.youtube_url:
            from urllib.parse import urlparse, parse_qs
            query = urlparse(self.youtube_url)
            if query.hostname in ['www.youtube.com', 'youtube.com']:
                return parse_qs(query.query).get('v', [None])[0]
            elif query.hostname == 'youtu.be':
                return query.path[1:]
        return None

    @property
    def duration(self):
        """Optional: Fetch duration using YouTube API if needed"""
        return None  # You can integrate YouTube Data API here
