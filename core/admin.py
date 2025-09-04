from django.contrib import admin
from .models import UploadedContent, UserProfile, Ad  # Add Ad to imports
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

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

# Your existing admin classes below...
@admin.register(UploadedContent)
class UploadedContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('content_type', 'uploaded_at')
    search_fields = ('title', 'uploaded_by__username')
    ordering = ('-uploaded_at',)
    date_hierarchy = 'uploaded_at'

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('role', 'subject_specialization', 'bio', 'phone_number', 'location', 'profile_picture', 'is_verified')
    readonly_fields = ('created_at', 'updated_at')

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'is_active')
    list_filter = ('profile__role', 'is_staff', 'is_active', 'profile__subject_specialization')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__bio')
    
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'No Role'
    get_role.short_description = 'Role'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'role', 'subject_specialization', 'is_verified', 'created_at')
    list_filter = ('role', 'subject_specialization', 'is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'bio')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_verified',)
    actions = ['make_teacher', 'verify_teachers', 'make_student']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'
    
    def make_teacher(self, request, queryset):
        updated = queryset.update(role='teacher')
        self.message_user(request, f'{updated} users were successfully marked as teachers.')
    make_teacher.short_description = "Mark selected users as Teachers"
    
    def verify_teachers(self, request, queryset):
        updated = queryset.filter(role='teacher').update(is_verified=True)
        self.message_user(request, f'{updated} teachers were successfully verified.')
    verify_teachers.short_description = "Verify selected Teachers"
    
    def make_student(self, request, queryset):
        updated = queryset.update(role='student', is_verified=False)
        self.message_user(request, f'{updated} users were successfully marked as students.')
    make_student.short_description = "Mark selected users as Students"

# Unregister the default User admin and register with custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)