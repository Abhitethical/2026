from django.shortcuts import render
from . models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import transaction
from .forms import CustomUserForm
from .forms import CustomerRegistrationForm
def home(request):
    return render(request,"index.html")



def productsearch(request):
    return render(request,"productsearch.html")



def login_page(request):

    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            customer = CustomerRegistration.objects.get(user=user)

            customer.last_login = user.last_login
            customer.login_time = timezone.now()
            customer.is_active = True
            customer.save()

            messages.success(request, "Logged in Successfully")
            return redirect("/")

        else:
            messages.error(request, "Invalid Username or Password")
            return redirect("/login")

    return render(request, "login.html")


def forgotpassword(request):
    return render(request,"forgotpassword.html")



from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction


def register(request):

    if request.method == "POST":

        user_form = CustomUserForm(request.POST)
        customer_form = CustomerRegistrationForm(
            request.POST,
            request.FILES
        )

        if user_form.is_valid() and customer_form.is_valid():

            with transaction.atomic():

                user = user_form.save()

                customer = customer_form.save(commit=False)
                customer.user = user
                customer.save()

            messages.success(request, "Registration successful!")
            return redirect("login")

    else:
        user_form = CustomUserForm()
        customer_form = CustomerRegistrationForm()

    return render(request, "register.html", {
        "user_form": user_form,
        "customer_form": customer_form,
    })



def register(request):

    if request.method == "POST":

        user_form = CustomUserForm(request.POST)
        customer_form = CustomerRegistrationForm(
            request.POST,
            request.FILES
        )

        if user_form.is_valid() and customer_form.is_valid():

            with transaction.atomic():

                user = user_form.save()

                customer = customer_form.save(commit=False)
                customer.user = user
                customer.save()

            messages.success(request, "Registration successful!")
            return redirect("login")

    else:
        user_form = CustomUserForm()
        customer_form = CustomerRegistrationForm()

    return render(request, "register.html", {
        "user_form": user_form,
        "customer_form": customer_form,
    })


def helpcenter(request):
    return render(request,"helpcenter.html")

def favviewpage(request):
    return render(request,"favviewpage.html")

def profile(request):
    return render(request,"profile.html") 

def logout(request):
    return render(request,"logout.html") 


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
    




