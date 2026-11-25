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
    path('return-detail/<int:pk>/',views.return_detail, name='return_detail'),
    path('forgot-password/',views.forgot_password,name='forgot_password'),
    path('reset-password/<str:token>/',views.reset_password,name='reset_password'),






    path("productsearch",views.productsearch, name="productsearch"),
    path("profile",views.profile, name="profile"),
    path("helpcenter",views.helpcenter, name="helpcenter"),
    path("contactus",views.contactus, name="contactus"),
    path("shipping",views.shipping, name="shipping"),
    path("returnpolicy",views.returnpolicy, name="returnpolicy"),
    path("privacypolicy",views.privacypolicy, name="privacypolicy"),
    path("termsconditions",views.termsconditions, name="termsconditions"),
    path("cookiepolicy",views.cookiepolicy, name="cookiepolicy"),











  path('step1/', views.seller_register_step1, name='seller_register_step1'),
  path('step2/<int:seller_id>/', views.seller_register_step2, name='seller_register_step2'),


  path('seller_login/', views.seller_login, name='seller_login'),
  path('unlock/', views.unlock_username, name='unlock_username'),
  path("seller/forgot-password/",views.seller_forgot_password,name="seller_forgot_password"),



]
