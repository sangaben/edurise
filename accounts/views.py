from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CustomUserCreationForm
from .models import UserProfile
from .forms import CustomUserCreationForm


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
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    """Renders the user profile page."""
    return render(request, 'accounts/profile.html')

@login_required
def logout_confirm(request):
    """Handles user logout confirmation."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('home')
    return render(request, 'accounts/logout.html')