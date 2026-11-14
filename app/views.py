from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

from .forms import CustomUserForm, CustomerRegistrationForm

def home(request):
    return render(request,"index.html")



def productsearch(request):
    return render(request,"productsearch.html")


def login(request):
    return render(request,"login.html")

def forgotpassword(request):
    return render(request,"forgotpassword.html")


def register(request):
    return render(request, 'register.html')



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
    




