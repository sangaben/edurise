# resources/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
import os
import uuid

def content_file_path(instance, filename):
    """Generate file path for uploaded content"""
    ext = filename.split('.')[-1]
    unique_id = uuid.uuid4().hex[:8]
    filename = f"{slugify(instance.title)}-{unique_id}.{ext}"
    return os.path.join('content', instance.content_type, filename)

class Subject(models.Model):
    """Subject/category for educational resources"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#4361ee', help_text="Hex color for subject badge")
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Subjects'
    
    def __str__(self):
        return self.name

class EducationLevel(models.Model):
    """Education level for resource targeting"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Education Levels'
    
    def __str__(self):
        return self.name

class UploadedContent(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('audio', 'Audio'),
        ('image', 'Image'),
        ('youtube', 'YouTube'),
        ('document', 'Document'),
        ('presentation', 'Presentation'),
        ('spreadsheet', 'Spreadsheet'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Core Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    content_type = models.CharField(
        max_length=15, 
        choices=CONTENT_TYPE_CHOICES,
        default='pdf'
    )
    
    # Categorization
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    education_levels = models.ManyToManyField(EducationLevel, blank=True)
    difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_LEVELS, default='beginner')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Media Content
    file = models.FileField(upload_to=content_file_path, blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True, help_text="Add YouTube video link here")
    cover_image = models.ImageField(
        upload_to='content/covers/',
        blank=True,
        null=True,
        help_text="Optional cover image for videos/audio"
    )
    thumbnail = models.ImageField(
        upload_to='content/thumbnails/',
        blank=True,
        null=True,
        help_text="Auto-generated thumbnail for videos"
    )
    
    # Metadata
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='uploaded_content'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status & Features
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    requires_login = models.BooleanField(default=False)
    
    # Statistics
    download_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    review_count = models.PositiveIntegerField(default=0)
    
    # Educational Metadata
    learning_objectives = models.TextField(blank=True, help_text="What students will learn")
    prerequisites = models.TextField(blank=True, help_text="Required prior knowledge")
    estimated_duration = models.PositiveIntegerField(default=0, help_text="Estimated time in minutes")
    curriculum_alignment = models.TextField(blank=True, help_text="How this aligns with curriculum")
    
    # Admin Fields
    featured_until = models.DateTimeField(null=True, blank=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_content'
    )
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Educational Resource'
        verbose_name_plural = 'Educational Resources'
        permissions = [
            ("can_feature_resource", "Can feature resource"),
            ("can_approve_resource", "Can approve resources"),
            ("can_export_resources", "Can export resources data"),
        ]
        indexes = [
            models.Index(fields=['status', 'is_public']),
            models.Index(fields=['content_type']),
            models.Index(fields=['uploaded_by', 'uploaded_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while UploadedContent.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        
        # Auto-set status for verified teachers
        if hasattr(self.uploaded_by, 'profile'):
            if self.uploaded_by.profile.role == 'teacher' and self.uploaded_by.profile.is_verified:
                if self.status == 'draft':
                    self.status = 'approved'
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('resource_detail', kwargs={'slug': self.slug})

    def clean(self):
        """Validate model data"""
        errors = {}
        
        # YouTube content must have YouTube URL
        if self.content_type == 'youtube' and not self.youtube_url:
            errors['youtube_url'] = 'YouTube URL is required for YouTube content type.'
        
        # Non-YouTube content must have a file
        if self.content_type != 'youtube' and not self.file:
            errors['file'] = 'File is required for non-YouTube content types.'
        
        # File size validation (50MB limit)
        if self.file and self.file.size > 50 * 1024 * 1024:
            errors['file'] = 'File size must be less than 50MB.'
        
        if errors:
            raise ValidationError(errors)

    # Property Methods
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
    def file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1][1:].lower()
        return None

    @property
    def file_size_mb(self):
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return 0

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def is_under_review(self):
        return self.status == 'under_review'

    @property
    def tag_list(self):
        """Return tags as list"""
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []

    # Action Methods
    def increment_download_count(self):
        self.download_count += 1
        self.save(update_fields=['download_count', 'updated_at'])

    def increment_views_count(self):
        self.views_count += 1
        self.save(update_fields=['views_count', 'updated_at'])

    def increment_like_count(self):
        self.like_count += 1
        self.save(update_fields=['like_count', 'updated_at'])

    def increment_share_count(self):
        self.share_count += 1
        self.save(update_fields=['share_count', 'updated_at'])

    def update_rating(self, new_rating):
        """Update average rating when new review is added"""
        total_rating = (self.average_rating * self.review_count) + new_rating
        self.review_count += 1
        self.average_rating = total_rating / self.review_count
        self.save(update_fields=['average_rating', 'review_count', 'updated_at'])

    def approve(self, reviewed_by=None, notes=""):
        """Approve this resource"""
        self.status = 'approved'
        self.last_reviewed_at = timezone.now()
        if reviewed_by:
            self.reviewed_by = reviewed_by
        self.review_notes = notes
        self.save()

    def reject(self, reviewed_by=None, notes=""):
        """Reject this resource"""
        self.status = 'rejected'
        self.last_reviewed_at = timezone.now()
        if reviewed_by:
            self.reviewed_by = reviewed_by
        self.review_notes = notes
        self.save()

    # Display Methods
    def get_difficulty_badge_color(self):
        colors = {
            'beginner': 'success',
            'intermediate': 'warning',
            'advanced': 'danger'
        }
        return colors.get(self.difficulty_level, 'secondary')

    def get_status_badge_color(self):
        colors = {
            'draft': 'secondary',
            'under_review': 'warning',
            'approved': 'success',
            'rejected': 'danger'
        }
        return colors.get(self.status, 'secondary')

class ResourceReview(models.Model):
    """Reviews and ratings for resources"""
    resource = models.ForeignKey(UploadedContent, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['resource', 'user']
        ordering = ['-created_at']
        verbose_name_plural = 'Resource Reviews'

    def __str__(self):
        return f"{self.user.username} - {self.resource.title} ({self.rating} stars)"

class DownloadHistory(models.Model):
    """Track download history"""
    resource = models.ForeignKey(UploadedContent, on_delete=models.CASCADE, related_name='download_history')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-downloaded_at']
        verbose_name_plural = 'Download History'

    def __str__(self):
        return f"{self.resource.title} - {self.downloaded_at}"