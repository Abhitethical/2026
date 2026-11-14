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


def register(request):
    return render(request,"register.html")
    



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
    




