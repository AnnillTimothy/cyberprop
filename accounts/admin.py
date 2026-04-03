from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_verified', 'is_staff']
    list_filter = ['role', 'is_verified', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('role', 'phone', 'avatar', 'bio', 'company_name', 'is_verified')}),
    )
