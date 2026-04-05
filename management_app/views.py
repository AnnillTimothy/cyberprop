from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from properties.models import Property

from .forms import (
    CleaningScheduleForm,
    ExpenseForm,
    IncomeForm,
    MaintenanceRequestForm,
)
from .models import (
    CleaningSchedule,
    Expense,
    Income,
    MaintenanceRequest,
    OwnerPayout,
)


def staff_or_admin(user):
    return user.role in ('staff', 'admin')


@login_required
def management_overview(request):
    if not staff_or_admin(request.user):
        return render(request, 'management_app/overview.html', {'access_denied': True})

    properties = Property.objects.all()
    total_properties = properties.count()
    company_properties = properties.filter(ownership_type='company').count()
    investor_properties = properties.filter(ownership_type='investor').count()

    total_income = Income.objects.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    net_profit = total_income - total_expenses

    open_maintenance = MaintenanceRequest.objects.filter(status__in=['open', 'in_progress']).count()
    upcoming_cleaning = CleaningSchedule.objects.filter(status='scheduled').count()
    pending_payouts = OwnerPayout.objects.filter(status='pending').count()

    recent_income = Income.objects.select_related('property')[:5]
    recent_expenses = Expense.objects.select_related('property')[:5]
    recent_maintenance = MaintenanceRequest.objects.select_related('property')[:5]

    context = {
        'total_properties': total_properties,
        'company_properties': company_properties,
        'investor_properties': investor_properties,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'open_maintenance': open_maintenance,
        'upcoming_cleaning': upcoming_cleaning,
        'pending_payouts': pending_payouts,
        'recent_income': recent_income,
        'recent_expenses': recent_expenses,
        'recent_maintenance': recent_maintenance,
    }
    return render(request, 'management_app/overview.html', context)


@login_required
def property_financials(request, pk):
    if not staff_or_admin(request.user):
        return render(request, 'management_app/overview.html', {'access_denied': True})

    prop = get_object_or_404(Property, pk=pk)
    incomes = Income.objects.filter(property=prop)
    expenses = Expense.objects.filter(property=prop)

    total_income = incomes.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    net = total_income - total_expenses

    payouts = OwnerPayout.objects.filter(property=prop) if prop.ownership_type == 'investor' else None
    total_management_fees = payouts.aggregate(total=Sum('management_fee'))['total'] if payouts else 0

    context = {
        'property': prop,
        'incomes': incomes[:10],
        'expenses': expenses[:10],
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net': net,
        'payouts': payouts,
        'total_management_fees': total_management_fees or 0,
    }
    return render(request, 'management_app/property_financials.html', context)


@login_required
def expense_list(request, pk):
    if not staff_or_admin(request.user):
        return render(request, 'management_app/overview.html', {'access_denied': True})

    prop = get_object_or_404(Property, pk=pk)
    expenses = Expense.objects.filter(property=prop)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.property = prop
            expense.created_by = request.user
            expense.save()
            return redirect('management:expenses', pk=pk)
    else:
        form = ExpenseForm(initial={'property': prop})

    context = {
        'property': prop,
        'expenses': expenses,
        'form': form,
        'total': expenses.aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'management_app/expense_list.html', context)


@login_required
def income_list(request, pk):
    if not staff_or_admin(request.user):
        return render(request, 'management_app/overview.html', {'access_denied': True})

    prop = get_object_or_404(Property, pk=pk)
    incomes = Income.objects.filter(property=prop)

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.property = prop
            income.save()
            return redirect('management:income', pk=pk)
    else:
        form = IncomeForm(initial={'property': prop})

    context = {
        'property': prop,
        'incomes': incomes,
        'form': form,
        'total': incomes.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'management_app/income_list.html', context)


@login_required
def maintenance_list(request):
    if not staff_or_admin(request.user):
        return render(request, 'management_app/overview.html', {'access_denied': True})

    status_filter = request.GET.get('status', '')
    requests_qs = MaintenanceRequest.objects.select_related('property', 'reported_by')
    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)

    context = {
        'maintenance_requests': requests_qs,
        'status_filter': status_filter,
    }
    return render(request, 'management_app/maintenance_list.html', context)


@login_required
def maintenance_create(request):
    if not staff_or_admin(request.user):
        return render(request, 'management_app/overview.html', {'access_denied': True})

    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.reported_by = request.user
            maintenance.save()
            return redirect('management:maintenance')
    else:
        form = MaintenanceRequestForm()

    return render(request, 'management_app/maintenance_form.html', {'form': form})


@login_required
def payout_list(request):
    if not staff_or_admin(request.user):
        return render(request, 'management_app/overview.html', {'access_denied': True})

    payouts = OwnerPayout.objects.select_related('property', 'owner')
    status_filter = request.GET.get('status', '')
    if status_filter:
        payouts = payouts.filter(status=status_filter)

    total_payouts = payouts.filter(status='paid').aggregate(total=Sum('net_payout'))['total'] or 0
    total_fees = payouts.aggregate(total=Sum('management_fee'))['total'] or 0

    context = {
        'payouts': payouts,
        'status_filter': status_filter,
        'total_payouts': total_payouts,
        'total_fees': total_fees,
    }
    return render(request, 'management_app/payout_list.html', context)


@login_required
def cleaning_list(request):
    if not staff_or_admin(request.user):
        return render(request, 'management_app/overview.html', {'access_denied': True})

    schedules = CleaningSchedule.objects.select_related('property')
    status_filter = request.GET.get('status', '')
    if status_filter:
        schedules = schedules.filter(status=status_filter)

    context = {
        'schedules': schedules,
        'status_filter': status_filter,
    }
    return render(request, 'management_app/cleaning_list.html', context)
