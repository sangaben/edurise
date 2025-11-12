# resources/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import UploadedContent

@admin.register(UploadedContent)
class UploadedContentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'content_type_display', 
        'uploaded_by', 
        'uploaded_at', 
        'download_count', 
        'views_count',
        'is_featured',
        'status_badge'
    )
    
    list_filter = (
        'content_type', 
        'uploaded_at', 
        'is_featured',
        'uploaded_by'
    )
    
    search_fields = (
        'title', 
        'description', 
        'uploaded_by__username',
        'uploaded_by__first_name',
        'uploaded_by__last_name'
    )
    
    list_editable = ('is_featured',)
    
    readonly_fields = (
        'uploaded_at', 
        'updated_at', 
        'download_count', 
        'views_count',
        'slug',
        'file_preview',
        'youtube_embed'
    )
    
    ordering = ('-uploaded_at',)
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'slug',
                'description',
                'content_type',
                'is_featured'
            )
        }),
        ('Media Content', {
            'fields': (
                'file',
                'youtube_url',
                'cover_image',
                'file_preview',
                'youtube_embed'
            )
        }),
        ('Uploader Information', {
            'fields': (
                'uploaded_by',
            )
        }),
        ('Statistics & Metadata', {
            'fields': (
                'download_count',
                'views_count',
                'uploaded_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def content_type_display(self, obj):
        """Display content type with colored badges"""
        type_colors = {
            'video': 'primary',
            'pdf': 'danger',
            'audio': 'info',
            'image': 'success',
            'youtube': 'warning'
        }
        color = type_colors.get(obj.content_type, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_content_type_display()
        )
    content_type_display.short_description = 'Type'
    
    def status_badge(self, obj):
        """Display status badge"""
        if obj.content_type == 'youtube' and obj.youtube_url:
            return format_html('<span class="badge bg-success">✓ YouTube</span>')
        elif obj.file:
            return format_html('<span class="badge bg-info">✓ File</span>')
        else:
            return format_html('<span class="badge bg-warning">⚠ No Media</span>')
    status_badge.short_description = 'Status'
    
    def file_preview(self, obj):
        """Show file preview if available"""
        if obj.file:
            if obj.content_type == 'image':
                return format_html(
                    '<img src="{}" style="max-width: 200px; max-height: 150px;" />',
                    obj.file.url
                )
            elif obj.content_type in ['pdf', 'video', 'audio']:
                return format_html(
                    '<a href="{}" target="_blank" class="btn btn-sm btn-outline-primary">View File</a>',
                    obj.file.url
                )
        return "No file uploaded"
    file_preview.short_description = 'File Preview'
    
    def youtube_embed(self, obj):
        """Show YouTube embed if available"""
        if obj.content_type == 'youtube' and obj.youtube_id:
            return format_html(
                '<iframe width="200" height="150" src="https://www.youtube.com/embed/{}" frameborder="0" allowfullscreen></iframe>',
                obj.youtube_id
            )
        return "No YouTube video"
    youtube_embed.short_description = 'YouTube Preview'
    
    def get_queryset(self, request):
        """Optimize queryset for admin"""
        return super().get_queryset(request).select_related('uploaded_by')
    
    def save_model(self, request, obj, form, change):
        """Set uploaded_by when creating new content"""
        if not obj.pk:  # If creating a new object
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    # Admin actions
    actions = ['make_featured', 'reset_download_count', 'export_resources']
    
    def make_featured(self, request, queryset):
        """Admin action to mark resources as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} resources marked as featured.')
    make_featured.short_description = "Mark selected resources as featured"
    
    def reset_download_count(self, request, queryset):
        """Admin action to reset download counts"""
        updated = queryset.update(download_count=0)
        self.message_user(request, f'{updated} resources download counts reset.')
    reset_download_count.short_description = "Reset download counts for selected resources"
    
    def export_resources(self, request, queryset):
        """Admin action to export resources data (placeholder)"""
        self.message_user(request, f'Export functionality for {queryset.count()} resources would be implemented here.')
    export_resources.short_description = "Export selected resources data"

    # Custom admin CSS
    class Media:
        css = {
            'all': ('admin/css/resources_admin.css',)
        }