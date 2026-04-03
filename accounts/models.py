from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('property_owner', 'Property Owner'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email or self.username

    @property
    def is_tenant(self):
        return self.role == 'tenant'

    @property
    def is_property_owner(self):
        return self.role == 'property_owner'

    @property
    def is_staff_member(self):
        return self.role == 'staff'

    @property
    def is_admin_user(self):
        return self.role == 'admin'
