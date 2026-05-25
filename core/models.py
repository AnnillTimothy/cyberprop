from django.db import models


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, help_text='Internal notes from the team')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} — {self.subject or 'No subject'}"


class SiteSettings(models.Model):
    """Singleton model for site-wide editable content."""

    # Hero
    hero_title = models.CharField(max_length=200, default='Next-Gen Property Management')
    hero_subtitle = models.TextField(
        default=(
            'CyberProp combines cutting-edge technology with expert property management '
            'to deliver seamless experiences for tenants, owners, and investors.'
        )
    )

    # Stats (displayed on the homepage counter section)
    stat_properties = models.CharField(max_length=20, default='150+')
    stat_properties_label = models.CharField(max_length=60, default='Properties Managed')
    stat_tenants = models.CharField(max_length=20, default='500+')
    stat_tenants_label = models.CharField(max_length=60, default='Happy Tenants')
    stat_occupancy = models.CharField(max_length=20, default='98%')
    stat_occupancy_label = models.CharField(max_length=60, default='Occupancy Rate')
    stat_portfolio = models.CharField(max_length=20, default='R50M+')
    stat_portfolio_label = models.CharField(max_length=60, default='Portfolio Value')

    # About / Mission
    about_tagline = models.CharField(max_length=200, default='Smart property management for the modern era')
    about_mission_title = models.CharField(max_length=200, default='Our Mission')
    about_mission_text = models.TextField(
        default=(
            'CyberProp was founded with a simple vision: to revolutionise property management '
            'in South Africa through technology. We believe that managing properties should be '
            'transparent, efficient, and accessible to everyone — from individual landlords to '
            'large-scale investors.'
        )
    )
    about_mission_text_2 = models.TextField(
        blank=True,
        default=(
            'Our platform combines decades of property management expertise with cutting-edge '
            'software to deliver an experience that benefits tenants, property owners, and '
            'investors alike.'
        )
    )
    about_established = models.CharField(max_length=20, default='Est. 2024')
    about_location = models.CharField(max_length=100, default='Cape Town, South Africa')

    # Contact info
    contact_email = models.EmailField(default='info@cyberprop.co.za')
    contact_phone = models.CharField(max_length=30, default='+27 21 000 0000')
    contact_address = models.TextField(
        default='CyberProp Property Management\nCape Town, Western Cape\nSouth Africa'
    )
    contact_hours_weekday = models.CharField(max_length=60, default='Monday – Friday: 08:00 – 17:00')
    contact_hours_saturday = models.CharField(max_length=60, default='Saturday: 09:00 – 13:00')

    # CTA Section
    cta_title = models.CharField(max_length=200, default='Ready to Get Started?')
    cta_subtitle = models.TextField(
        default=(
            'Whether you\'re looking for a rental, want your property managed, or interested '
            'in investing — CyberProp has you covered.'
        )
    )

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
