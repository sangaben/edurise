from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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