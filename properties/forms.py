from django import forms
from .models import Enquiry, Booking, PropertySubmission, Property


class PropertySearchForm(forms.Form):
    city = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'City', 'class': 'form-control'}),
    )
    property_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Property.PROPERTY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    min_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Price', 'class': 'form-control'}),
    )
    max_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Max Price', 'class': 'form-control'}),
    )
    bedrooms = forms.ChoiceField(
        required=False,
        choices=[('', 'Any'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5+')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (optional)'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your message...'}),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['viewing_date', 'notes']
        widgets = {
            'viewing_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
            ),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests...'}),
        }


class PropertySubmissionForm(forms.ModelForm):
    class Meta:
        model = PropertySubmission
        exclude = ['owner', 'status', 'admin_notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'proposed_rent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes...'}),
        }
