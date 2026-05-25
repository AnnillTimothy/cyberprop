from django.contrib import admin

from .models import SiteSettings, ContactMessage


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle'),
        }),
        ('Stats', {
            'fields': (
                'stat_properties', 'stat_properties_label',
                'stat_tenants', 'stat_tenants_label',
                'stat_occupancy', 'stat_occupancy_label',
                'stat_portfolio', 'stat_portfolio_label',
            ),
        }),
        ('About / Mission', {
            'fields': (
                'about_tagline', 'about_mission_title',
                'about_mission_text', 'about_mission_text_2',
                'about_established', 'about_location',
            ),
        }),
        ('Contact Info', {
            'fields': (
                'contact_email', 'contact_phone',
                'contact_address',
                'contact_hours_weekday', 'contact_hours_saturday',
            ),
        }),
        ('CTA Section', {
            'fields': ('cta_title', 'cta_subtitle'),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at', 'updated_at')

