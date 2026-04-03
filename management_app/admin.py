from django.contrib import admin

from .models import (
    CleaningSchedule,
    Expense,
    Income,
    MaintenanceRequest,
    OwnerPayout,
)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('property', 'category', 'amount', 'date', 'created_by')
    list_filter = ('category', 'date', 'property__ownership_type')
    search_fields = ('description', 'property__title')
    date_hierarchy = 'date'


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('property', 'income_type', 'amount', 'date', 'is_paid', 'tenant')
    list_filter = ('income_type', 'is_paid', 'date')
    search_fields = ('description', 'property__title')
    date_hierarchy = 'date'


@admin.register(OwnerPayout)
class OwnerPayoutAdmin(admin.ModelAdmin):
    list_display = ('property', 'owner', 'period_month', 'rent_collected', 'management_fee', 'net_payout', 'status')
    list_filter = ('status', 'period_month')
    search_fields = ('property__title', 'owner__username', 'reference')


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'property', 'priority', 'status', 'reported_by', 'created_at')
    list_filter = ('priority', 'status')
    search_fields = ('title', 'description', 'property__title')


@admin.register(CleaningSchedule)
class CleaningScheduleAdmin(admin.ModelAdmin):
    list_display = ('property', 'scheduled_date', 'scheduled_time', 'cleaner_name', 'status', 'cost')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('property__title', 'cleaner_name')
