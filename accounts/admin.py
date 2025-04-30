from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_active', 'email_verified', 'is_staff')
    list_filter = ('is_active', 'email_verified', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'email_verified', 'verification_token', 'account_locked')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
