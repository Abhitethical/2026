from django.shortcuts import render

def home(request):
    return render(request,"index.html")



def productsearch(request):
    return render(request,"productsearch.html")

def login(request):
    return render(request,"login.html")


