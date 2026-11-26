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






from django import forms
from django.contrib.auth.password_validation import validate_password


class SellerForgotPasswordForm(forms.Form):

    email = forms.EmailField(
        label="Registered Email",
        max_length=255,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your registered email",
                "autocomplete": "off",
                "autocapitalize": "none",
                "spellcheck": "false",
            }
        )
    )


class SellerResetPasswordForm(forms.Form):

    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter new password",
                "autocomplete": "new-password",
                "spellcheck": "false",
            }
        )
    )

    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm new password",
                "autocomplete": "new-password",
                "spellcheck": "false",
            }
        )
    )

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm:

            if password != confirm:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

            try:
                validate_password(password)

            except forms.ValidationError as error:
                raise forms.ValidationError(error.messages)

        return cleaned_data





from django import forms
from .models import Advertisementx


class AdvertisementForm(forms.ModelForm):

    class Meta:

        model = Advertisementx

        fields = [
            "title",
            "product_image",
            "video",
            "thumbnail",
            "start_date",
            "end_date",
            "description",
            "plan",
        ]


        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Advertisement Title"
                }
            ),


            "product_image": forms.FileInput(
                attrs={
                    "class": "form-control"
                }
            ),


            "video": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "video/mp4"
                }
            ),


            "thumbnail": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*"
                }
            ),


            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),


            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),


            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Advertisement Description"
                }
            ),


            "plan": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "plan"
                }
            ),
        }



    # Video Validation

    def clean_video(self):

        video = self.cleaned_data.get("video")


        if video:

            # Check size 100MB

            size = video.size / (1024 * 1024)


            if size > 100:

                raise forms.ValidationError(
                    "Maximum video size allowed is 100 MB"
                )


            # Check MP4

            extension = video.name.split(".")[-1].lower()


            if extension != "mp4":

                raise forms.ValidationError(
                    "Only MP4 video format is supported"
                )


        return video



    # Date Validation

    def clean(self):

        cleaned_data = super().clean()


        start = cleaned_data.get(
            "start_date"
        )

        end = cleaned_data.get(
            "end_date"
        )


        if start and end:

            if end < start:

                raise forms.ValidationError(
                    "End date must be after start date"
                )




