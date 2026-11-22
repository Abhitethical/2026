from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name="home"),
    path('register',views.register,name="register"),
    path('login',views.login_page,name="login"),
    path('logout',views.logout_page,name="logout"),
    path('carted',views.cart_paged,name="carted"),
    path('orderstatus/', views.orderstatus, name='orderstatus'), 
    path('fav',views.fav_page,name="fav"),
    path('favviewpage',views.favviewpage,name="favviewpage"),
    path('remove_fav/<str:fid>',views.remove_fav,name="remove_fav"),
    path('remove_cart/<str:cid>',views.remove_cart,name="remove_cart"),
    path('collections',views.collections,name="collections"),
    path('collections/<str:name>',views.collectionsview,name="collections"),
    path('collections/<str:cname>/<str:pname>',views.product_details,name="product_details"),
    path('addtocart',views.add_to_cart,name="addtocart"),
    path('checkouts/', views.checkouts, name='checkoutview'),
    path('order/<int:pk>/', views.order_detail, name='orderdetail'),  
    path('add-review/<int:order_id>/', views.add_review, name='add_review'),
    path("return/<int:order_id>/", views.create_return_request, name="return_request"),
    path('my-returns/',views.customer_return_list,name='customer_return_list'),





    path("productsearch",views.productsearch, name="productsearch"),
    path("profile",views.profile, name="profile"),
    path("forgotpassword",views.forgotpassword, name="forgotpassword"),
    path("helpcenter",views.helpcenter, name="helpcenter"),
    path("contactus",views.contactus, name="contactus"),
    path("shipping",views.shipping, name="shipping"),
    path("returnpolicy",views.returnpolicy, name="returnpolicy"),
    path("privacypolicy",views.privacypolicy, name="privacypolicy"),
    path("termsconditions",views.termsconditions, name="termsconditions"),
    path("cookiepolicy",views.cookiepolicy, name="cookiepolicy"),
]
