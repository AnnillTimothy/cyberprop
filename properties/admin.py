from django.contrib import admin
from .models import Property, PropertyImage, Booking, Enquiry, PropertySubmission


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'ownership_type', 'status', 'monthly_rent', 'city', 'is_featured', 'is_approved')
    list_filter = ('ownership_type', 'status', 'property_type', 'is_featured', 'is_approved', 'city')
    search_fields = ('title', 'address', 'city', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PropertyImageInline]


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'caption', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'viewing_date', 'status', 'created_at')
    list_filter = ('status', 'viewing_date')
    search_fields = ('property__title', 'user__username', 'user__email')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'property', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'property__title')


@admin.register(PropertySubmission)
class PropertySubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'property_type', 'proposed_rent', 'status', 'created_at')
    list_filter = ('status', 'property_type')
    search_fields = ('title', 'owner__username', 'owner__email')
