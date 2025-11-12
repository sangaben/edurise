from django.contrib import admin
from .models import Ad

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'is_active', 'start_date', 'end_date', 'created_at')
    list_filter = ('position', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    fieldsets = (
        ('Ad Content', {
            'fields': ('title', 'description', 'image', 'target_url', 'cta_text')
        }),
        ('Display Settings', {
            'fields': ('position', 'is_active', 'show_timer', 'start_date', 'end_date')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)