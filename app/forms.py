from pyexpat import model
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class CustomUserForm(UserCreationForm):
  username=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter User Name'}))
  email=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Email Address'}))
  password1=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter Your Password'}))
  password2=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter Confirm Password'}))
  class Meta:
    model=User

    fields=['username','email','password1','password2']

    fields=['username','email','password1','password2']





from django import forms
from django.core.exceptions import ValidationError
import re

# Country, State, and City choices (ideally you'd load these dynamically or model them)
COUNTRY_CHOICES = [
    ('', 'Select Country'),
    ('India', 'India'),
    ('USA', 'USA'),
    ('UK', 'UK'),
]

STATE_CHOICES = [
     ('', 'Select State'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
    ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
    ('Chandigarh', 'Chandigarh'),
    ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('Delhi', 'Delhi'),
    ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ('Ladakh', 'Ladakh'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Puducherry', 'Puducherry'),
]

CITY_CHOICES = [
    ('', 'Select District'),
    ('Alappuzha', 'Alappuzha'),
    ('Ernakulam', 'Ernakulam'),
    ('Idukki', 'Idukki'),
    ('Kannur', 'Kannur'),
    ('Kasaragod', 'Kasaragod'),
    ('Kollam', 'Kollam'),
    ('Kottayam', 'Kottayam'),
    ('Kozhikode', 'Kozhikode'),
    ('Malappuram', 'Malappuram'),
    ('Palakkad', 'Palakkad'),
    ('Pathanamthitta', 'Pathanamthitta'),
    ('Thiruvananthapuram', 'Thiruvananthapuram'),
    ('Thrissur', 'Thrissur'),
    ('Wayanad', 'Wayanad'),

]

class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'})
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )
    address_line1 = forms.CharField(
        max_length=255,
        label="Address Line 1",
        widget=forms.TextInput(attrs={'placeholder': 'Street address, P.O. box, etc.'})
    )
    address_line2 = forms.CharField(
        max_length=255,
        required=False,
        label="Address Line 2",
        widget=forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit, etc. (optional)'})
    )
    
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        label="Country"
    )
    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        label="State"
    )
    city = forms.ChoiceField(
        choices=CITY_CHOICES,
        label="City"
    )

    postal_code = forms.CharField(
        max_length=6,
        label="Postal Code",
        widget=forms.TextInput(attrs={'placeholder': '6-digit PIN/ZIP code'})
    )
    phone = forms.CharField(
        max_length=10,
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': '10-digit phone number'})
    )

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if not re.match(r'^\d{6}$', postal_code):
            raise ValidationError("Postal code must be exactly 6 digits.")
        return postal_code

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^\d{10}$', phone):
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone


from django import forms
from .models import ReturnRequested

class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnRequested
        fields = ["reason", "description", "image", "video"]



