from pyexpat import model
from PIL import Image, UnidentifiedImageError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomerRegistration


class CustomUserForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter User Name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Email Address'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Your Password'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")

        return email


from django import forms
from PIL import Image, UnidentifiedImageError
from .models import CustomerRegistration


class CustomerRegistrationForm(forms.ModelForm):

    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter Phone Number',
                'inputmode': 'numeric',
                'maxlength': '10',
                'autocomplete': 'off'
            }
        )
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter Address',
                'rows': 3,
                'autocomplete': 'off'
            }
        )
    )

    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/webp'
            }
        )
    )

    class Meta:
        model = CustomerRegistration
        fields = ['profile_image', 'phone', 'address']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()

        # Only digits
        if not phone.isdigit():
            raise forms.ValidationError(
                "Phone number must contain only numbers."
            )

        # Indian 10-digit mobile number
        if len(phone) != 10:
            raise forms.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        if phone[0] not in "6789":
            raise forms.ValidationError(
                "Enter a valid mobile number."
            )

        return phone

    def clean_profile_image(self):
        uploaded_file = self.cleaned_data.get('profile_image')

        if not uploaded_file:
            return uploaded_file

        # -----------------------------------------
        # 1. Maximum file size: 5 MB
        # -----------------------------------------
        MAX_SIZE = 5 * 1024 * 1024

        if uploaded_file.size > MAX_SIZE:
            raise forms.ValidationError(
                "Profile image must be smaller than 5 MB."
            )

        # -----------------------------------------
        # 2. Check extension
        # -----------------------------------------
        allowed_extensions = {
            'jpg',
            'jpeg',
            'png',
            'webp'
        }

        filename = uploaded_file.name.lower()

        if '.' not in filename:
            raise forms.ValidationError(
                "Invalid image filename."
            )

        extension = filename.rsplit('.', 1)[1]

        if extension not in allowed_extensions:
            raise forms.ValidationError(
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        # -----------------------------------------
        # 3. Check actual image content with Pillow
        # -----------------------------------------
        try:
            uploaded_file.seek(0)

            image = Image.open(uploaded_file)

            # Verify image structure
            image.verify()

            uploaded_file.seek(0)

            # Open again after verify()
            image = Image.open(uploaded_file)

            # -----------------------------------------
            # 4. Verify actual detected format
            # -----------------------------------------
            allowed_formats = {
                'JPEG',
                'PNG',
                'WEBP'
            }

            if image.format not in allowed_formats:
                raise forms.ValidationError(
                    "The uploaded file is not a supported image format."
                )

            # -----------------------------------------
            # 5. Prevent decompression-bomb images
            # -----------------------------------------
            MAX_PIXELS = 20_000_000

            if image.width * image.height > MAX_PIXELS:
                raise forms.ValidationError(
                    "Image dimensions are too large."
                )

            # -----------------------------------------
            # 6. Force complete image loading
            # -----------------------------------------
            image.load()

        except (UnidentifiedImageError, OSError, ValueError):
            raise forms.ValidationError(
                "The uploaded file is corrupted or is not a valid image."
            )

        finally:
            uploaded_file.seek(0)

        return uploaded_file

