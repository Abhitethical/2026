from django.shortcuts import render

def home(request):
    return render(request,"index.html")



def productsearch(request):
    return render(request,"productsearch.html")

def login(request):
    return render(request,"login.html")


def register(request):
    return render(request,"register.html")


def favviewpage(request):
    return render(request,"favviewpage.html")


def carted(request):
    return render(request,"carted.html")


def orderstatus(request):
    return render(request,"orderstatus.html")


def login(request):
    return render(request,"login.html")


def login(request):
    return render(request,"login.html")
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
    




