from django.shortcuts import render
from django.shortcuts import redirect, render
from django.http import  JsonResponse
from .forms import CustomUserForm
from . models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
import json

def home(request):
    return render(request,"index.html")



def productsearch(request):
    return render(request,"productsearch.html")


def login(request):
    return render(request,"login.html")






import io
import os
import uuid
import logging

from PIL import Image, UnidentifiedImageError

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.http import Http404
from django.shortcuts import redirect, render
from django.core.files.base import ContentFile

from .forms import CustomUserForm, CustomerRegistrationForm
from .models import CustomerRegistration

logger = logging.getLogger(__name__)


def register(request):

    # -----------------------------------------
    # Already logged-in users
    # -----------------------------------------
    if request.user.is_authenticated:
        return redirect("/")

    user_form = CustomUserForm()
    customer_form = CustomerRegistrationForm()

    if request.method == "POST":

        user_form = CustomUserForm(request.POST)

        customer_form = CustomerRegistrationForm(
            request.POST,
            request.FILES
        )

        if user_form.is_valid() and customer_form.is_valid():

            try:

                # =========================================
                # CREATE USER
                # =========================================
                user = user_form.save(commit=False)

                user.email = user_form.cleaned_data["email"]

                user.save()

                # =========================================
                # CREATE CUSTOMER
                # =========================================
                customer = customer_form.save(commit=False)

                customer.user = user
                customer.email = user.email

                # =========================================
                # SECURE PROFILE IMAGE PROCESSING
                # =========================================
                uploaded_image = customer_form.cleaned_data.get(
                    "profile_image"
                )

                if uploaded_image:

                    secure_image = secure_profile_image(
                        uploaded_image
                    )

                    customer.profile_image.save(
                        secure_image["name"],
                        secure_image["file"],
                        save=False
                    )

                customer.save()

                # =========================================
                # SEND EMAIL
                # =========================================
                try:

                    send_registration_email(user)

                except Exception as email_error:

                    logger.exception(
                        "Registration email failed: %s",
                        email_error
                    )

                    messages.warning(
                        request,
                        "Registration successful, but email could not be sent."
                    )

                messages.success(
                    request,
                    "Registration Successful! Please Login."
                )

                return redirect("/login")

            except Exception as e:

                logger.exception(
                    "Customer registration failed: %s",
                    e
                )

                raise Http404(
                    "Something went wrong during registration."
                )

    context = {
        "user_form": user_form,
        "customer_form": customer_form,
    }

    return render(
        request,
        "register.html",
        context
    )

def forgotpassword(request):
    return render(request,"forgotpassword.html")


def favviewpage(request):
    return render(request,"favviewpage.html")

def carted(request):
    return render(request,"carted.html") 
def orderstatus(request):
    return render(request,"orderstatus.html")





def helpcenter(request):
    return render(request,"helpcenter.html")
    
def contactus(request):
    return render(request, 'contactus.html')

def shipping(request):
    return render(request, 'shipping.html')
def returnpolicy(request):
    return render(request, 'returnpolicy.html')

def privacypolicy(request):
    return render(request, 'privacypolicy.html')

def termsconditions(request):
    return render(request, 'termsconditions.html')
def cookiepolicy(request):
    return render(request, 'cookiepolicy.html')
    




