from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from PIL import Image, UnidentifiedImageError

from .models import CustomerRegistration


class CustomUserForm(UserCreationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter User Name",
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Email Address",
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Your Password",
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm Password",
        })
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "This email is already registered."
            )

        return email


class CustomerRegistrationForm(forms.ModelForm):

    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Phone Number",
            "inputmode": "numeric",
            "maxlength": "10",
            "autocomplete": "off",
        })
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Enter Address",
            "rows": 3,
            "autocomplete": "off",
        })
    )

    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": "image/jpeg,image/png,image/webp",
        })
    )

    class Meta:
        model = CustomerRegistration
        fields = ["profile_image", "phone", "address"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if not phone.isdigit():
            raise ValidationError(
                "Phone number must contain only numbers."
            )

        if len(phone) != 10:
            raise ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        if phone[0] not in "6789":
            raise ValidationError(
                "Enter a valid Indian mobile number."
            )

        return phone

    def clean_profile_image(self):
        uploaded_file = self.cleaned_data.get("profile_image")

        if not uploaded_file:
            return uploaded_file

        max_size = 5 * 1024 * 1024

        if uploaded_file.size > max_size:
            raise ValidationError(
                "Profile image must be smaller than 5 MB."
            )

        allowed_extensions = {"jpg", "jpeg", "png", "webp"}
        extension = uploaded_file.name.lower().rsplit(".", 1)

        if len(extension) != 2 or extension[1] not in allowed_extensions:
            raise ValidationError(
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        try:
            uploaded_file.seek(0)

            image = Image.open(uploaded_file)
            image.verify()

            uploaded_file.seek(0)
            image = Image.open(uploaded_file)

            if image.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValidationError(
                    "Unsupported image format."
                )

            if image.width * image.height > 20_000_000:
                raise ValidationError(
                    "Image dimensions are too large."
                )

            image.load()

        except ValidationError:
            raise

        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
        ):
            raise ValidationError(
                "The uploaded file is corrupted or invalid."
            )

        finally:
            uploaded_file.seek(0)

        return uploaded_file
