from django.db import models
from django.conf import settings


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('bond', 'Bond Payment'),
        ('utilities', 'Utilities'),
        ('insurance', 'Insurance'),
        ('rates_taxes', 'Rates & Taxes'),
        ('cleaning', 'Cleaning Service'),
        ('other', 'Other'),
    ]
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=300)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.category} - {self.property.title} - R{self.amount}"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Investor properties can only have cleaning expenses
        if self.property.ownership_type == 'investor' and self.category not in ('cleaning', 'other'):
            raise ValidationError(
                "Investor properties can only have cleaning or other service expenses tracked by CyberProp."
            )


class Income(models.Model):
    INCOME_TYPE_CHOICES = [
        ('rent', 'Rent Payment'),
        ('deposit', 'Deposit'),
        ('late_fee', 'Late Fee'),
        ('other', 'Other'),
    ]
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='incomes')
    income_type = models.CharField(max_length=20, choices=INCOME_TYPE_CHOICES, default='rent')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=300, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.income_type} - {self.property.title} - R{self.amount}"


class OwnerPayout(models.Model):
    """Track payouts to investor property owners"""
    STATUS_CHOICES = [('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')]

    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='payouts')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payouts')
    period_month = models.DateField(help_text="First day of the month this payout covers")
    rent_collected = models.DecimalField(max_digits=12, decimal_places=2)
    management_fee = models.DecimalField(max_digits=12, decimal_places=2)
    cleaning_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_payout = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_date = models.DateField(null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_month']
        unique_together = ['property', 'period_month']

    def __str__(self):
        return f"Payout to {self.owner} for {self.property} - {self.period_month}"

    def save(self, *args, **kwargs):
        self.net_payout = self.rent_collected - self.management_fee - self.cleaning_deductions
        super().save(*args, **kwargs)


class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='maintenance_requests')
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='maintenance_reports'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    assigned_to = models.CharField(max_length=200, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.property.title}"


class CleaningSchedule(models.Model):
    STATUS_CHOICES = [('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]

    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='cleaning_schedules')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    cleaner_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"Cleaning: {self.property.title} on {self.scheduled_date}"
