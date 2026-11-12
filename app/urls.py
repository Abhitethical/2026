from django.urls import path
from . import views

urlpatterns=[
    path("",views.home, name="home"),
    path("productsearch",views.productsearch, name="productsearch"),
    path("login",views.login, name="login"),
 
]