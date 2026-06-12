from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ActivityLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'avatar_initials')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'email', 'first_name', 'last_name')}),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'description')
    readonly_fields = ('user', 'action', 'description', 'timestamp', 'ip_address')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
