from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone

from .models import UploadedContent, Ad, UserProfile
from .forms import CustomUserCreationForm


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
    
    return render(request, 'home.html', context)


@login_required
def upload(request):
    """
    Handles content upload for verified teachers only.
    """
    # Check if user is a verified teacher
    if not (hasattr(request.user, 'profile') and 
            request.user.profile.role == 'teacher' and 
            request.user.profile.is_verified):
        messages.error(request, 'Only verified teachers can upload resources.')
        return redirect('home')
    
    # Your upload logic here
    return render(request, 'upload.html')


def search(request):
    """
    Handles search functionality across uploaded content.
    Searches in title and description fields.
    """
    query = request.GET.get('q', '')
    results = UploadedContent.objects.all().order_by('-uploaded_at')
    
    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    context = {
        'contents': results,
        'query': query,
        'title': f'EduRise | Search: {query}',
        'page_heading': f'Search Results for "{query}"',
        'is_search': True,
    }
    return render(request, 'home.html', context)


def about(request):
    """Renders the about page."""
    return render(request, 'about.html')


def courses(request):
    """Renders the courses page."""
    return render(request, 'courses.html')


def resources(request):
    """Renders the resources page."""
    return render(request, 'resources.html')


@login_required
def profile(request):
    """Renders the user profile page."""
    return render(request, 'profile.html')


def register(request):
    """Handles user registration with role selection."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Set the user role from the form
            role = form.cleaned_data.get('role', 'student')
            user.userprofile.role = role
            user.userprofile.save()
            
            login(request, user)
            messages.success(request, f'Registration successful! Welcome to EduRise as a {role}.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})


@login_required
def logout_confirm(request):
    """Handles user logout confirmation."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('home')
    return render(request, 'logout.html')