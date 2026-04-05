from django import forms

from .models import (
    CleaningSchedule,
    Expense,
    Income,
    MaintenanceRequest,
    OwnerPayout,
)


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        exclude = ['created_by', 'created_at']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(attrs={'placeholder': 'Expense description'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        exclude = ['created_at']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(attrs={'placeholder': 'Income description'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        exclude = ['reported_by', 'created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'completed_date': forms.DateInput(attrs={'type': 'date'}),
            'estimated_cost': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'actual_cost': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }


class CleaningScheduleForm(forms.ModelForm):
    class Meta:
        model = CleaningSchedule
        exclude = ['created_at', 'completed_at']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'cost': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }


class OwnerPayoutForm(forms.ModelForm):
    class Meta:
        model = OwnerPayout
        exclude = ['created_at']
        widgets = {
            'period_month': forms.DateInput(attrs={'type': 'date'}),
            'paid_date': forms.DateInput(attrs={'type': 'date'}),
            'rent_collected': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'management_fee': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'cleaning_deductions': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'net_payout': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }
