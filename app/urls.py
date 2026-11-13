from django.urls import path
from . import views

urlpatterns=[
    path("",views.home, name="home"),
    path("productsearch",views.productsearch, name="productsearch"),
    path("login",views.login, name="login"),

    path("register",views.register, name="register"),
    path("favviewpage",views.favviewpage, name="favviewpage"),
    path("carted",views.login, name="carted"),
    path("orderstatus",views.login, name="orderstatus"),
    path("login",views.login, name="login"),


    path("helpcenter",views.helpcenter, name="helpcenter"),



    path("contactus",views.contactus, name="contactus"),
    path("shipping",views.shipping, name="shipping"),
    path("returnpolicy",views.returnpolicy, name="helpcenter"),
    path("privacypolicy",views.helpcenter, name="helpcenter"),
    path("termsconditions",views.termsconditions, name="termsconditions"),
    path("cookiepolicy",views.cookiepolicy, name="cookiepolicy"),
]
