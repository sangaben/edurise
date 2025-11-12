from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import UploadedContent
from .forms import UploadedContentForm

def resources(request):
    """Renders the resources page."""
    contents = UploadedContent.objects.all().order_by('-uploaded_at')
    context = {
        'contents': contents,
    }
    return render(request, 'resources/resources.html', context)

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
    return render(request, 'resources/upload.html')