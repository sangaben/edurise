from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Course, Category

from .forms import CourseForm

def courses(request):
    categories = Category.objects.all()
    courses = Course.objects.filter(is_active=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(courses, 6)  # Show 6 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'courses': page_obj,
        'categories': categories,
    }
    return render(request, 'courses/courses.html', context)

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    context = {
        'course': course,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is already enrolled
    if course.enrolled_students.filter(id=request.user.id).exists():
        messages.info(request, 'You are already enrolled in this course.')
    else:
        # Add user to enrolled_students
        course.enrolled_students.add(request.user)
        messages.success(request, f'Successfully enrolled in {course.title}!')
    
    return redirect('course_detail', slug=course.slug)