from django.shortcuts import render
from django.db.models import Q

from resources.models import UploadedContent
from courses.models import Course

def search(request):
    """
    Handles search functionality across uploaded content and courses.
    Searches in title and description fields.
    """
    query = request.GET.get('q', '')
    content_results = UploadedContent.objects.all().order_by('-uploaded_at')
    course_results = Course.objects.filter(is_active=True).order_by('-created_at')
    
    if query:
        content_results = content_results.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
        course_results = course_results.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    context = {
        'content_results': content_results,
        'course_results': course_results,
        'query': query,
        'title': f'EduRise | Search: {query}',
        'page_heading': f'Search Results for "{query}"',
    }
    return render(request, 'search/search.html', context)