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
 
]