from django.shortcuts import render, redirect
from django.contrib import messages

from properties.models import Property
from .models import SiteSettings


def home(request):
    """Homepage with featured properties and GSAP hero."""
    featured_properties = Property.objects.filter(
        is_approved=True, is_featured=True
    ).order_by('-created_at')[:6]
    settings = SiteSettings.get()
    return render(request, 'core/home.html', {
        'featured_properties': featured_properties,
        'settings': settings,
    })


def about(request):
    """About CyberProp page."""
    settings = SiteSettings.get()
    return render(request, 'core/about.html', {'settings': settings})


def contact(request):
    """Contact page with basic form handling."""
    settings = SiteSettings.get()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        if name and email and message_text:
            messages.success(
                request,
                'Thank you for your message! We will get back to you shortly.',
            )
        else:
            messages.error(request, 'Please fill in all required fields.')

    return render(request, 'core/contact.html', {'settings': settings})


def terms(request):
    """Terms and conditions page."""
    return render(request, 'core/terms.html')


def privacy(request):
    """Privacy policy page."""
    return render(request, 'core/privacy.html')


def cookies(request):
    """Cookies policy page."""
    return render(request, 'core/cookies.html')
