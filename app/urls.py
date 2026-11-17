from django.urls import path
from . import views

urlpatterns=[
    path("",views.home, name="home"),
    path("productsearch",views.productsearch, name="productsearch"),
    path("login",views.login_page, name="login"),

    path("register",views.register, name="register"),
    path('logout',views.logout_page,name="logout"),

    path("forgotpassword",views.forgotpassword, name="forgotpassword"),

    path("profile",views.profile, name="profile"),
    path("favviewpage",views.favviewpage, name="favviewpage"),
    path("carted",views.login, name="carted"),
    path("orderstatus",views.login, name="orderstatus"),
    path("login",views.login, name="login"),


    path("helpcenter",views.helpcenter, name="helpcenter"),



    path("contactus",views.contactus, name="contactus"),
    path("shipping",views.shipping, name="shipping"),
    path("returnpolicy",views.returnpolicy, name="returnpolicy"),
    path("privacypolicy",views.privacypolicy, name="privacypolicy"),
    path("termsconditions",views.termsconditions, name="termsconditions"),
    path("cookiepolicy",views.cookiepolicy, name="cookiepolicy"),
]
