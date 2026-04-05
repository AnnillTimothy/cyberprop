from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Property, PropertySubmission
from .forms import PropertySearchForm, EnquiryForm, BookingForm, PropertySubmissionForm


def property_list(request):
    """Show approved, available/featured properties with search/filter."""
    properties = Property.objects.filter(
        Q(is_approved=True),
        Q(status='available') | Q(is_featured=True),
    )

    form = PropertySearchForm(request.GET)
    if form.is_valid():
        city = form.cleaned_data.get('city')
        property_type = form.cleaned_data.get('property_type')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        bedrooms = form.cleaned_data.get('bedrooms')

        if city:
            properties = properties.filter(city__icontains=city)
        if property_type:
            properties = properties.filter(property_type=property_type)
        if min_price is not None:
            properties = properties.filter(monthly_rent__gte=min_price)
        if max_price is not None:
            properties = properties.filter(monthly_rent__lte=max_price)
        if bedrooms:
            if bedrooms == '5':
                properties = properties.filter(bedrooms__gte=5)
            else:
                properties = properties.filter(bedrooms=int(bedrooms))

    return render(request, 'properties/property_list.html', {
        'properties': properties,
        'form': form,
    })


def property_detail(request, slug):
    """Show single property with images, enquiry form, booking form."""
    prop = get_object_or_404(Property, slug=slug, is_approved=True)
    images = prop.images.all()
    enquiry_form = EnquiryForm()
    booking_form = BookingForm()

    return render(request, 'properties/property_detail.html', {
        'property': prop,
        'images': images,
        'enquiry_form': enquiry_form,
        'booking_form': booking_form,
    })


def submit_enquiry(request, slug):
    """Handle enquiry form submission."""
    prop = get_object_or_404(Property, slug=slug, is_approved=True)

    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.property = prop
            enquiry.save()
            messages.success(request, 'Your enquiry has been submitted. We will get back to you soon!')
            return redirect('properties:detail', slug=slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        return redirect('properties:detail', slug=slug)

    images = prop.images.all()
    return render(request, 'properties/property_detail.html', {
        'property': prop,
        'images': images,
        'enquiry_form': form,
        'booking_form': BookingForm(),
    })


@login_required
def book_viewing(request, slug):
    """Handle booking form submission."""
    prop = get_object_or_404(Property, slug=slug, is_approved=True)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.property = prop
            booking.user = request.user
            booking.save()
            messages.success(request, 'Your viewing has been booked! We will confirm shortly.')
            return redirect('properties:detail', slug=slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        return redirect('properties:detail', slug=slug)

    images = prop.images.all()
    return render(request, 'properties/property_detail.html', {
        'property': prop,
        'images': images,
        'enquiry_form': EnquiryForm(),
        'booking_form': form,
    })


@login_required
def submit_property(request):
    """Property owners submit properties for management by CyberProp."""
    if not request.user.is_property_owner:
        messages.error(request, 'Only property owners can submit properties.')
        return redirect('properties:list')

    if request.method == 'POST':
        form = PropertySubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.owner = request.user
            submission.save()
            messages.success(request, 'Your property has been submitted for review!')
            return redirect('properties:my_submissions')
    else:
        form = PropertySubmissionForm()

    return render(request, 'properties/submit_property.html', {'form': form})


@login_required
def my_submissions(request):
    """View own property submissions and their status."""
    submissions = PropertySubmission.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'properties/my_submissions.html', {'submissions': submissions})
