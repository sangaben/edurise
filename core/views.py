from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

from courses.models import Course, Category
from resources.models import UploadedContent
from .models import Ad
from .forms import AdForm

def home(request):
    """
    Renders the homepage with a list of uploaded educational content
    sorted by most recent first and active ads.
    """
    contents = UploadedContent.objects.all().order_by('-uploaded_at')
    
    # Get active ads for each position
    now = timezone.now()
    ads = {
        'top_ad': Ad.objects.filter(
            position='top', 
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first(),
        'mid_content_ad': Ad.objects.filter(
            position='mid_content', 
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first(),
        'sidebar_ad': Ad.objects.filter(
            position='sidebar', 
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first(),
        'sidebar_bottom_ad': Ad.objects.filter(
            position='sidebar_bottom', 
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first(),
        'bottom_ad': Ad.objects.filter(
            position='bottom', 
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first(),
    }
    
    context = {
        'contents': contents,
        'ads': ads,
        'title': 'EduRise | Learn Anywhere',
        'page_heading': 'Latest Educational Content',
    }
    
    return render(request, 'core/home.html', context)

def about(request):
    """Renders the about page."""
    return render(request, 'core/about.html')