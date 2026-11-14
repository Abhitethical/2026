from django.shortcuts import render
<<<<<<< HEAD

=======
>>>>>>> 1c59691 (Update complete Django project)

def home(request):
    return render(request,"index.html")



def productsearch(request):
    return render(request,"productsearch.html")


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
    




