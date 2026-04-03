from django.db import models

from django.db import models
from django.conf import settings


class Property(models.Model):
    OWNERSHIP_CHOICES = [('company', 'Company Owned'), ('investor', 'Investor Owned')]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('tenanted', 'Tenanted'),
        ('maintenance', 'Under Maintenance'),
        ('pending', 'Pending Approval'),
    ]
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('townhouse', 'Townhouse'),
        ('villa', 'Villa'),
        ('studio', 'Studio'),
        ('penthouse', 'Penthouse'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    ownership_type = models.CharField(max_length=20, choices=OWNERSHIP_CHOICES, default='company')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='owned_properties',
    )

    # Location
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)

    # Details
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    parking_spaces = models.PositiveIntegerField(default=0)
    size_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Pricing
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Fees for investor properties
    management_fee_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        help_text="Management fee percentage for investor properties",
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    # Media
    featured_image = models.ImageField(upload_to='properties/', blank=True, null=True)

    # Amenities as text
    amenities = models.TextField(blank=True, help_text="Comma-separated amenities")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Current tenant
    current_tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='rented_properties',
    )

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.status == 'available' and self.is_approved

    @property
    def management_fee_amount(self):
        return (self.monthly_rent * self.management_fee_percent) / 100

    @property
    def owner_payout(self):
        """Amount paid to investor after fees"""
        if self.ownership_type == 'investor':
            return self.monthly_rent - self.management_fee_amount
        return None

    def get_amenities_list(self):
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.title}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    viewing_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewing_date']

    def __str__(self):
        return f"Booking: {self.user} - {self.property} on {self.viewing_date}"


class Enquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='enquiries')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Enquiries"
        ordering = ['-created_at']

    def __str__(self):
        return f"Enquiry from {self.name} about {self.property}"


class PropertySubmission(models.Model):
    """Property owners submit properties for CyberProp to manage"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions',
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=Property.PROPERTY_TYPE_CHOICES)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    proposed_rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, help_text="Additional notes from the owner")
    admin_notes = models.TextField(blank=True, help_text="Notes from CyberProp admin")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission: {self.title} by {self.owner}"
