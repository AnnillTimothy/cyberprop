from datetime import date
from decimal import Decimal

from django import forms as django_forms
from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Q, Count
from django.forms import inlineformset_factory
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import CustomUser
from core.models import ContactMessage
from properties.models import Property, PropertyImage, Booking, Enquiry, PropertySubmission
from management_app.models import (
    Expense, Income, MaintenanceRequest, CleaningSchedule, OwnerPayout,
)
from store.models import Order, OrderItem

from .forms import (
    UserAdminForm, UserCreateForm, PropertyAdminForm, SubmissionReviewForm,
)


def staff_required(view_func):
    """Decorator that checks the user is staff/admin."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings
            from django.shortcuts import redirect as _r
            return _r(f"{settings.LOGIN_URL}?next={request.path}")
        if request.user.role not in ('staff', 'admin') and not request.user.is_superuser:
            return HttpResponseForbidden('Access denied.')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Dashboard Home ──────────────────────────────────────────────────────────

@login_required
@staff_required
def dashboard_home(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_properties = Property.objects.count()
    total_tenants = CustomUser.objects.filter(role='tenant').count()
    revenue_this_month = (
        Income.objects.filter(date__gte=month_start, is_paid=True)
        .aggregate(total=Sum('amount'))['total']
    ) or Decimal('0.00')
    pending_maintenance = MaintenanceRequest.objects.filter(
        status__in=['open', 'in_progress']
    ).count()
    pending_enquiries = Enquiry.objects.filter(is_read=False).count()
    total_orders = Order.objects.count()
    pending_contact_messages = ContactMessage.objects.filter(status='new').count()

    recent_bookings = Booking.objects.select_related('property', 'user').order_by('-created_at')[:5]
    recent_enquiries = Enquiry.objects.select_related('property').order_by('-created_at')[:5]
    recent_maintenance = MaintenanceRequest.objects.select_related('property').order_by('-created_at')[:5]
    recent_contact_messages = ContactMessage.objects.order_by('-created_at')[:5]

    # Monthly income/expense data for charts (last 6 months)
    months_data = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        m_start = date(y, m, 1)
        if m == 12:
            m_end = date(y + 1, 1, 1)
        else:
            m_end = date(y, m + 1, 1)
        inc = Income.objects.filter(date__gte=m_start, date__lt=m_end, is_paid=True).aggregate(t=Sum('amount'))['t'] or 0
        exp = Expense.objects.filter(date__gte=m_start, date__lt=m_end).aggregate(t=Sum('amount'))['t'] or 0
        months_data.append({
            'label': m_start.strftime('%b %Y'),
            'income': float(inc),
            'expense': float(exp),
        })

    context = {
        'total_properties': total_properties,
        'total_tenants': total_tenants,
        'revenue_this_month': revenue_this_month,
        'pending_maintenance': pending_maintenance,
        'pending_enquiries': pending_enquiries,
        'total_orders': total_orders,
        'pending_contact_messages': pending_contact_messages,
        'recent_bookings': recent_bookings,
        'recent_enquiries': recent_enquiries,
        'recent_maintenance': recent_maintenance,
        'recent_contact_messages': recent_contact_messages,
        'months_data': months_data,
    }
    return render(request, 'dashboard/home.html', context)


# ─── Users ───────────────────────────────────────────────────────────────────

@login_required
@staff_required
def user_list(request):
    qs = CustomUser.objects.all().order_by('-date_joined')
    q = request.GET.get('q', '')
    role = request.GET.get('role', '')
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
    if role:
        qs = qs.filter(role=role)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/user_list.html', {
        'users': page, 'q': q, 'role': role,
    })


@login_required
@staff_required
def user_detail(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UserAdminForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            return redirect('dashboard:user_list')
    else:
        form = UserAdminForm(instance=user_obj)
    return render(request, 'dashboard/user_form.html', {'form': form, 'edit': True, 'user_obj': user_obj})


@login_required
@staff_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:user_list')
    else:
        form = UserCreateForm()
    return render(request, 'dashboard/user_form.html', {'form': form, 'edit': False})


# ─── Properties ──────────────────────────────────────────────────────────────

@login_required
@staff_required
def property_admin_list(request):
    qs = Property.objects.all().order_by('-created_at')
    status = request.GET.get('status', '')
    ownership = request.GET.get('ownership_type', '')
    if status:
        qs = qs.filter(status=status)
    if ownership:
        qs = qs.filter(ownership_type=ownership)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/property_list.html', {'properties': page, 'status': status, 'ownership': ownership})


@login_required
@staff_required
def property_admin_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    ImageFormSet = inlineformset_factory(
        Property, PropertyImage,
        fields=['image', 'caption', 'is_primary'],
        extra=3, can_delete=True,
        widgets={
            'caption': django_forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Caption (optional)'}),
            'is_primary': django_forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    )
    if request.method == 'POST':
        form = PropertyAdminForm(request.POST, request.FILES, instance=prop)
        image_formset = ImageFormSet(request.POST, request.FILES, instance=prop, prefix='images')
        if form.is_valid() and image_formset.is_valid():
            p = form.save(commit=False)
            if not p.slug:
                p.slug = slugify(p.title)
            p.save()
            image_formset.save()
            django_messages.success(request, 'Property saved successfully.')
            return redirect('dashboard:property_detail', pk=pk)
    else:
        form = PropertyAdminForm(instance=prop)
        image_formset = ImageFormSet(instance=prop, prefix='images')

    bookings = prop.bookings.all().order_by('-created_at')[:10]
    maintenance = prop.maintenance_requests.all().order_by('-created_at')[:10]
    incomes = prop.incomes.all().order_by('-date')[:10]
    expenses = prop.expenses.all().order_by('-date')[:10]
    property_images = prop.images.all()

    return render(request, 'dashboard/property_detail_admin.html', {
        'property': prop, 'form': form, 'image_formset': image_formset,
        'bookings': bookings, 'maintenance': maintenance,
        'incomes': incomes, 'expenses': expenses,
        'property_images': property_images,
    })


@login_required
@staff_required
def property_admin_create(request):
    ImageFormSet = inlineformset_factory(
        Property, PropertyImage,
        fields=['image', 'caption', 'is_primary'],
        extra=3, can_delete=True,
        widgets={
            'caption': django_forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Caption (optional)'}),
            'is_primary': django_forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    )
    if request.method == 'POST':
        form = PropertyAdminForm(request.POST, request.FILES)
        image_formset = ImageFormSet(request.POST, request.FILES, prefix='images')
        if form.is_valid() and image_formset.is_valid():
            prop = form.save(commit=False)
            base_slug = slugify(prop.title)
            slug = base_slug
            n = 1
            while Property.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            prop.slug = slug
            prop.save()
            image_formset.instance = prop
            image_formset.save()
            return redirect('dashboard:property_list')
    else:
        form = PropertyAdminForm()
        image_formset = ImageFormSet(prefix='images')
    return render(request, 'dashboard/property_form.html', {'form': form, 'image_formset': image_formset, 'edit': False})


@login_required
@staff_required
def property_admin_delete(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        prop.delete()
        return redirect('dashboard:property_list')
    return HttpResponseForbidden('POST required.')


# ─── Submissions ─────────────────────────────────────────────────────────────

@login_required
@staff_required
def submission_list(request):
    qs = PropertySubmission.objects.all().select_related('owner').order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/submission_list.html', {'submissions': page, 'status': status})


@login_required
@staff_required
def submission_review(request, pk):
    submission = get_object_or_404(PropertySubmission, pk=pk)
    if request.method == 'POST':
        form = SubmissionReviewForm(request.POST)
        if form.is_valid():
            submission.status = form.cleaned_data['status']
            submission.admin_notes = form.cleaned_data['admin_notes']
            submission.save()

            if form.cleaned_data['status'] == 'approved':
                base_slug = slugify(submission.title)
                slug = base_slug
                n = 1
                while Property.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{n}"
                    n += 1
                Property.objects.create(
                    title=submission.title,
                    slug=slug,
                    description=submission.description,
                    property_type=submission.property_type,
                    ownership_type='investor',
                    owner=submission.owner,
                    address=submission.address,
                    city=submission.city,
                    province=submission.province,
                    bedrooms=submission.bedrooms,
                    bathrooms=submission.bathrooms,
                    monthly_rent=submission.proposed_rent,
                    management_fee_percent=form.cleaned_data['management_fee_percent'],
                    is_approved=True,
                )
            return redirect('dashboard:submission_list')
    else:
        form = SubmissionReviewForm()
    return render(request, 'dashboard/submission_review.html', {'submission': submission, 'form': form})


# ─── Bookings ────────────────────────────────────────────────────────────────

@login_required
@staff_required
def booking_list(request):
    qs = Booking.objects.all().select_related('property', 'user').order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/booking_list.html', {'bookings': page, 'status': status})


@login_required
@staff_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ('confirmed', 'cancelled', 'completed'):
            booking.status = new_status
            booking.save()
    return redirect('dashboard:booking_list')


# ─── Enquiries ───────────────────────────────────────────────────────────────

@login_required
@staff_required
def enquiry_list(request):
    qs = Enquiry.objects.all().select_related('property').order_by('-created_at')
    if request.method == 'POST':
        eid = request.POST.get('enquiry_id')
        if eid:
            Enquiry.objects.filter(pk=eid).update(is_read=True)
            return redirect('dashboard:enquiry_list')
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/enquiry_list.html', {'enquiries': page})


# ─── Orders ──────────────────────────────────────────────────────────────────

@login_required
@staff_required
def order_admin_list(request):
    qs = Order.objects.all().select_related('user').order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/order_list.html', {'orders': page, 'status': status})


@login_required
@staff_required
def order_admin_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = ['pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']
        if new_status in valid:
            order.status = new_status
            order.save()
            return redirect('dashboard:order_detail', pk=pk)
    items = order.items.select_related('product').all()
    return render(request, 'dashboard/order_detail_admin.html', {'order': order, 'items': items})


# ─── Reports ─────────────────────────────────────────────────────────────────

@login_required
@staff_required
def reports(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_income = Income.objects.filter(is_paid=True).aggregate(t=Sum('amount'))['t'] or Decimal('0')
    total_expenses = Expense.objects.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    month_income = Income.objects.filter(date__gte=month_start, is_paid=True).aggregate(t=Sum('amount'))['t'] or Decimal('0')
    month_expenses = Expense.objects.filter(date__gte=month_start).aggregate(t=Sum('amount'))['t'] or Decimal('0')

    total_props = Property.objects.count()
    tenanted = Property.objects.filter(status='tenanted').count()
    occupancy_rate = round((tenanted / total_props * 100), 1) if total_props else 0

    top_properties = (
        Property.objects.annotate(total_income=Sum('incomes__amount'))
        .order_by('-total_income')[:10]
    )

    pending_payouts = OwnerPayout.objects.filter(status='pending').aggregate(t=Sum('net_payout'))['t'] or Decimal('0')

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': total_income - total_expenses,
        'month_income': month_income,
        'month_expenses': month_expenses,
        'month_net': month_income - month_expenses,
        'occupancy_rate': occupancy_rate,
        'total_props': total_props,
        'tenanted': tenanted,
        'top_properties': top_properties,
        'pending_payouts': pending_payouts,
    }
    return render(request, 'dashboard/reports.html', context)



# ─── Contact Messages ────────────────────────────────────────────────────────

@login_required
@staff_required
def contact_message_list(request):
    qs = ContactMessage.objects.all().order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/contact_message_list.html', {
        'messages_qs': page, 'status': status,
        'status_choices': ContactMessage.STATUS_CHOICES,
    })


@login_required
@staff_required
def contact_message_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '').strip()
        valid_statuses = [s[0] for s in ContactMessage.STATUS_CHOICES]
        if new_status in valid_statuses:
            msg.status = new_status
        msg.admin_notes = admin_notes
        msg.save()
        django_messages.success(request, 'Contact message updated.')
        return redirect('dashboard:contact_message_detail', pk=pk)
    return render(request, 'dashboard/contact_message_detail.html', {
        'contact_msg': msg,
        'status_choices': ContactMessage.STATUS_CHOICES,
    })
