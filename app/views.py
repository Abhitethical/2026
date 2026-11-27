from django.shortcuts import render
from . models import *
from django.http import  JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import transaction
from .forms import CustomUserForm
import json


def home(request):

    products = Product.objects.all()



    ads = Advertisementx.objects.filter(

        status__in=[
            "APPROVED",
            "RUNNING"
        ],

        payment_status="PAID",

        end_date__gte=timezone.now()

    ).order_by(

        "paid_at"

    )



    return render(

        request,

        "index.html",

        {

        "Producte":products,

        "banners":ads

        }

    )


def favviewpage(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,"fav.html",{"fav":fav})
  else:
    return redirect("/")

def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")




def cart_paged(request):
  if request.user.is_authenticated:
    cart=Cart.objects.filter(user=request.user)
    return render(request,"carted.html",{"cart":cart})
  else:
    return redirect("home")

def orderstatus(request):

    if request.user.is_authenticated:
        user = request.user

        orders = Placedorderxx.objects.filter(
            user=user
        ).order_by("-created_at")  # latest first
    else:
        orders = Placedorderxx.objects.none()

    return render(
        request,
        "orderstatus.html",
        {"orders": orders}
    )




def remove_cart(request,cid):
  cartitem=Cart.objects.get(id=cid)
  cartitem.delete()
  return redirect("/cart")



def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)


def add_to_cart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=data['product_qty']
      product_id=data['pid']
      #print(request.user.id)
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Cart.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quantity>=product_qty:
            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added to Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)

def logout_page(request):
  if request.user.is_authenticated:
    logout(request)
    messages.success(request,"Logged out Successfully")
  return redirect("/")


def login_page(request):
  if request.user.is_authenticated:
    return redirect("/")
  else:
    if request.method=='POST':
      name=request.POST.get('username')
      pwd=request.POST.get('password')
      user=authenticate(request,username=name,password=pwd)
      if user is not None:
        login(request,user)
        messages.success(request,"Logged in Successfully")
        return redirect("/")
      else:
        messages.error(request,"Invalid User Name or Password")
        return redirect("/login")
    return render(request,"login.html")

def register(request):
  form=CustomUserForm()
  if request.method=='POST':
    form=CustomUserForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request,"Registration Success You can Login Now..!")
      return redirect('/login')
  return render(request,"register.html",{'form':form})


def collections(request):
  catagory=Catagory.objects.filter(status=0)
  return render(request,"shop/collections.html",{"catagory":catagory})

def collectionsview(request,name):
  if(Catagory.objects.filter(name=name,status=0)):
      products=Product.objects.filter(category__name=name)
      return render(request,"products/index.html",{"products":products,"category_name":name})
  else:
    messages.warning(request,"No Such Catagory Found")
    return redirect('collections')


def product_details(request, cname, pname):

    # Check category
    category = Catagory.objects.filter(
        name=cname,
        status=0
    ).first()

    if not category:
        messages.error(request, "No Such Category Found")
        return redirect('collections')

    # Find product inside the selected category
    products = Product.objects.filter(
        category=category,
        name=pname,
        status=0
    ).first()

    if not products:
        messages.error(request, "No Such Product Found")
        return redirect('collections')

    # Get reviews for the exact product
    reviews = Review.objects.filter(
        product=products
    ).order_by('-created_at')

    return render(
        request,
        "products/productdetails.html",
        {
            "products": products,
            "reviews": reviews
        }
    )


from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import Cart, Placedorderxx, Product  # Make sure Product model is imported
from .forms import CheckoutForm
from django.db import transaction




from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import render, redirect

GST_RATE = Decimal("0.03")


def checkouts(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect("home")

    def calculate_totals(cart_items, discount=Decimal("0")):
        net = Decimal("0")

        for item in cart_items:
            net += Decimal(item.product.selling_price) * item.product_qty

        gst = net * GST_RATE
        grand = net + gst - discount

        return net, gst, max(grand, Decimal("0"))

    if request.method == "POST":
        step = request.POST.get("step")

        # ================= STEP 1 =================
        if step == "1":
            form = CheckoutForm(request.POST)

            if form.is_valid():
                request.session["checkout_data"] = form.cleaned_data

                net, gst, grand = calculate_totals(cart_items)

                return render(request, "checkout_confirm.html", {
                    "form_data": form.cleaned_data,
                    "cart_items": cart_items,
                    "net_total": net,
                    "gst_amount": gst,
                    "grand_total": grand,
                    "discount": Decimal("0"),
                    "coupon_message": ""
                })

            return render(request, "checkoutview.html", {"form": form})

        # ================= COUPON STEP =================
        elif step == "coupon":
            coupon_code = request.POST.get("coupon_code", "").strip()

            discount = Decimal("0")
            message = "Invalid Coupon"
            applied = False

            today = timezone.now().date()

            # one-time use check
            already_used = Placedorderxx.objects.filter(
                user=user,
                coupon_code=coupon_code,
                coupon_discount__gt=0
            ).exists()

            if already_used:
                net, gst, grand = calculate_totals(cart_items)

                return render(request, "checkout_confirm.html", {
                    "form_data": request.session.get("checkout_data"),
                    "cart_items": cart_items,
                    "net_total": net,
                    "gst_amount": gst,
                    "grand_total": grand,
                    "discount": Decimal("0"),
                    "coupon_message": "This coupon can be used only once",
                    "applied_coupon": ""
                })

            # check coupon
            for item in cart_items:
                product = item.product

                if product.coupon_code == coupon_code and product.coupon_active:

                    # ================= EXPIRED CHECK =================
                    if product.coupon_expiry and product.coupon_expiry < today:
                        message = "❌ This coupon has expired"
                        applied = False
                        break

                    # ================= VALID COUPON =================
                    if product.coupon_discount > 0:
                        discount = Decimal(str(product.coupon_discount))
                        message = f"Coupon Applied: -₹{discount}"
                        applied = True
                        break

            request.session["applied_coupon"] = coupon_code if applied else ""
            request.session["applied_discount"] = str(discount if applied else 0)

            net, gst, grand = calculate_totals(cart_items, discount if applied else 0)

            return render(request, "checkout_confirm.html", {
                "form_data": request.session.get("checkout_data"),
                "cart_items": cart_items,
                "net_total": net,
                "gst_amount": gst,
                "grand_total": grand,
                "discount": discount if applied else Decimal("0"),
                "coupon_message": message,
                "applied_coupon": coupon_code if applied else ""
            })

        # ================= STEP 2 =================
        elif step == "2":
            checkout_data = request.session.get("checkout_data")
            if not checkout_data:
                return redirect("checkouts")

            discount = Decimal(request.session.get("applied_discount", "0"))
            coupon_code = request.session.get("applied_coupon", "")

            save_coupon = coupon_code if discount > 0 else ""
            save_discount = discount if discount > 0 else Decimal("0")

            try:
                with transaction.atomic():

                    net, gst, grand = calculate_totals(cart_items, save_discount)

                    for item in cart_items:
                        product = item.product

                        if item.product_qty > product.quantity:
                            return render(request, "checkout_confirm.html", {
                                "error": f"Not enough stock for {product.name}",
                                "form_data": checkout_data,
                                "cart_items": cart_items
                            })

                        # final expiry safety check
                        today = timezone.now().date()
                        if product.coupon_expiry and product.coupon_expiry < today:
                            save_coupon = ""
                            save_discount = Decimal("0")

                        Placedorderxx.objects.create(
                            user=user,
                            product=product,
                            product_name=product.name,
                            product_image=product.product_image,
                            product_price=product.selling_price,
                            selling_price=product.original_price,
                            vendor=product.vendor,
                            quantity=item.product_qty,

                            name=checkout_data.get("full_name"),
                            address=checkout_data.get("address_line1"),
                            city=checkout_data.get("city"),
                            state=checkout_data.get("state"),
                            phone=checkout_data.get("phone"),
                            postal_code=checkout_data.get("postal_code"),

                            coupon_code=save_coupon,
                            coupon_discount=save_discount,

                            total_amount=grand
                        )

                        product.quantity -= item.product_qty
                        product.save()

                    cart_items.delete()

                    request.session.pop("checkout_data", None)
                    request.session.pop("applied_coupon", None)
                    request.session.pop("applied_discount", None)

                    return redirect("home")

            except Exception as e:
                return render(request, "checkout_confirm.html", {
                    "error": str(e),
                    "cart_items": cart_items,
                    "form_data": checkout_data
                })

    return render(request, "checkoutview.html", {
        "form": CheckoutForm()
    })



from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta

def order_detail(request, pk):
    order = get_object_or_404(Placedorderxx, id=pk, user=request.user)

    # Convert UTC → Local Time
    order.created_at = timezone.localtime(order.created_at)

    # ✅ Return logic
    can_return = False
    if order.status == "Completed" and order.delivered_at:
        delivered_local = timezone.localtime(order.delivered_at)

        if timezone.now() <= delivered_local + timedelta(days=7):
            can_return = True

    return render(request, "order_detail.html", {
        "order": order,
        "can_return": can_return
    })




# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Review, Placedorderxx

def add_review(request, order_id):
    order = get_object_or_404(Placedorderxx, id=order_id, user=request.user)

    # ✅ Only allow if completed
    if order.status != 'completed':
        messages.error(request, "You can review only after order is completed")
        return redirect('orderdetail', pk=order_id)

    # ✅ Prevent duplicate review
    if Review.objects.filter(order=order).exists():
        messages.error(request, "You already reviewed this product")
        return redirect('orderdetail', pk=order_id)

    # ✅ IMPORTANT FIX
    if not order.product:
        messages.error(request, "Product not available for this order")
        return redirect('orderdetail', pk=order_id)

    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        Review.objects.create(
            user=request.user,
            product=order.product,   # ✅ FIXED HERE
            order=order,
            rating=rating,
            comment=comment,
            image=image,
            video=video
        )

        messages.success(request, "Review submitted successfully")
        return redirect('orderdetail', pk=order_id)
    


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import ReturnRequestForm
from .models import ReturnRequested, Placedorderxx


@login_required
def create_return_request(request, order_id):

    order = get_object_or_404(
        Placedorderxx,
        id=order_id,
        user=request.user
    )


    # prevent duplicate return

    already_exists = ReturnRequested.objects.filter(
        order=order
    ).exists()


    if already_exists:
        messages.warning(
            request,
            "Return request already submitted."
        )

        return redirect(
            "customer_return_list"
        )



    if request.method == "POST":

        form = ReturnRequestForm(
            request.POST,
            request.FILES
        )


        if form.is_valid():

            return_obj = form.save(
                commit=False
            )


            return_obj.order = order

            return_obj.user = request.user


            # IMPORTANT
            # seller ownership

            return_obj.vendor = order.vendor



            # product details

            return_obj.product_name = order.product_name

            return_obj.product_image = order.product_image

            return_obj.selling_price = order.selling_price

            return_obj.quantity = order.quantity



            # customer details

            return_obj.name = order.name

            return_obj.address = order.address

            return_obj.phone = order.phone

            return_obj.postal_code = order.postal_code

            return_obj.city = order.city 

            return_obj.coupon_discount = order.coupon_discount

            return_obj.city = order.city

            return_obj.status = "requested"


            return_obj.save()



            messages.success(
                request,
                "Return request submitted successfully."
            )


            return redirect(
                "customer_return_list"
            )


    else:

        form = ReturnRequestForm()



    return render(
        request,
        "return_form.html",
        {
            "form":form,
            "order":order
        }
    )


@login_required
def customer_return_list(request):

    returns = ReturnRequested.objects.filter(
        user=request.user
    ).order_by('-id')

    return render(request, "customer_return_list.html", {
        "returns": returns
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ReturnRequested


@login_required
def return_detail(request, pk):

    return_request = get_object_or_404(
        ReturnRequested,
        id=pk,
        user=request.user
    )

    if request.method == "POST":

        if return_request.status == "pickup_scheduled":

            return_request.pickup_address = request.POST.get('pickup_address')
            return_request.pickup_date = request.POST.get('pickup_date')
            return_request.pickup_time_slot = request.POST.get('pickup_time_slot')
            return_request.pickup_reason = request.POST.get('pickup_reason')

            return_request.save()

        else:

            return_request.resubmit_reason = request.POST.get("resubmit_reason")
            return_request.resubmit_description = request.POST.get("resubmit_description")

            # image upload
            if request.FILES.get("resubmit_image"):
                return_request.resubmit_image = request.FILES["resubmit_image"]

            # video upload
            if request.FILES.get("resubmit_video"):
                return_request.resubmit_video = request.FILES["resubmit_video"]

            # change status
            return_request.status = "Resubmitted"

            return_request.save()

        return redirect("return_detail", pk=return_request.id)

    return render(request, "return_detail.html", {
        "return_request": return_request
    })


import secrets

from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from django.core.mail import send_mail
from django.conf import settings

from django.utils import timezone

from django.db import transaction

from .models import PasswordResetToken, PasswordResetLimit


# ---------------------------------------
# FORGOT PASSWORD
# ---------------------------------------

def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get('email', '').strip()

        user = User.objects.filter(
            email__iexact=email
        ).first()

        if not user:

            return render(
                request,
                'forgot_password.html',
                {
                    'error': 'Email address is not registered.'
                }
            )

        today = timezone.localdate()

        # Check daily reset limit
        reset_limit = PasswordResetLimit.objects.filter(
            user=user,
            reset_date=today
        ).first()

        if reset_limit and reset_limit.reset_count >= 3:

            return render(
                request,
                'accounts/forgot_password.html',
                {
                    'error': 'Daily password reset limit reached. Try again tomorrow.'
                }
            )

        # Invalidate previously issued unused tokens
        PasswordResetToken.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)

        # Generate secure token
        token = secrets.token_urlsafe(32)

        PasswordResetToken.objects.create(
            user=user,
            token=token
        )

        # Generate reset URL
        reset_link = request.build_absolute_uri(
            f'/reset-password/{token}/'
        )

        # Send email
        subject = 'Password Reset Request'

        message = f"""
Hello {user.username},

We received a request to reset your password.

Click the link below to reset your password:

{reset_link}

This link expires in 10 minutes.

If you did not request this, please ignore this email.
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )

        return render(
            request,
            'forgot_password.html',
            {
                'success': 'Password reset link has been sent to your email.'
            }
        )

    return render(
        request,
        'forgot_password.html'
    )


# ---------------------------------------
# RESET PASSWORD
# ---------------------------------------

def reset_password(request, token):

    reset_token = PasswordResetToken.objects.filter(
        token=token,
        is_used=False
    ).select_related('user').first()

    if not reset_token:

        return render(
            request,
            'reset_password.html',
            {
                'error': 'This password reset link is expired or invalid.'
            }
        )

    # Check 10-minute expiration
    expiry_time = reset_token.created_at + timedelta(minutes=10)

    if timezone.now() > expiry_time:

        reset_token.is_used = True
        reset_token.save(update_fields=['is_used'])

        return render(
            request,
            'reset_password.html',
            {
                'error': 'This password reset link is expired or invalid.'
            }
        )

    if request.method == "POST":

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not password or not confirm_password:

            return render(
                request,
                'reset_password.html',
                {
                    'error': 'Please enter both passwords.'
                }
            )

        if password != confirm_password:

            return render(
                request,
                'reset_password.html',
                {
                    'error': 'Passwords do not match.'
                }
            )

        if len(password) < 8:

            return render(
                request,
                'reset_password.html',
                {
                    'error': 'Password must contain at least 8 characters.'
                }
            )

        # Atomically check token and daily limit
        with transaction.atomic():

            locked_token = PasswordResetToken.objects.select_for_update().filter(
                pk=reset_token.pk,
                is_used=False
            ).first()

            if not locked_token:

                return render(
                    request,
                    'reset_password.html',
                    {
                        'error': 'This password reset link is expired or invalid.'
                    }
                )

            # Check expiration again
            if timezone.now() > locked_token.created_at + timedelta(minutes=10):

                locked_token.is_used = True
                locked_token.save(update_fields=['is_used'])

                return render(
                    request,
                    'reset_password.html',
                    {
                        'error': 'This password reset link is expired or invalid.'
                    }
                )

            user = User.objects.select_for_update().get(
                pk=locked_token.user_id
            )

            today = timezone.localdate()

            limit, created = PasswordResetLimit.objects.get_or_create(
                user=user,
                reset_date=today
            )

            # Lock daily limit row
            limit = PasswordResetLimit.objects.select_for_update().get(
                pk=limit.pk
            )

            if limit.reset_count >= 3:

                locked_token.is_used = True
                locked_token.save(update_fields=['is_used'])

                return render(
                    request,
                    'reset_password.html',
                    {
                        'error': 'Daily password reset limit reached. Try again tomorrow.'
                    }
                )

            # Update password
            user.password = make_password(password)

            user.save(update_fields=['password'])

            # Increase daily successful reset count
            limit.reset_count += 1

            limit.save(update_fields=['reset_count'])

            # Mark token as used
            locked_token.is_used = True

            locked_token.save(update_fields=['is_used'])

        return render(
            request,
            'password_reset_success.html',
            {
                'success': 'Your password has been changed successfully.'
            }
        )

    return render(
        request,
        'reset_password.html'
    )
































































def productsearch(request):
    return render(request,"productsearch.html")



def helpcenter(request):
    return render(request,"helpcenter.html")

def profile(request):
    return render(request,"profile.html") 


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




























from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import SellerProfile
import random
def seller_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            try:
                seller = SellerProfile.objects.get(user=user)
            except SellerProfile.DoesNotExist:
                messages.error(request, "You are not registered as a seller.")
                return redirect('seller_login')

            if seller.is_locked:
                messages.error(request, "Your account is locked. Contact admin.")
                return redirect('seller_login')

            if seller.status == 'approved':
                seller.login_attempts = 0
                seller.save()
                login(request, user)
                return redirect('seller_dashboard')
            elif seller.status == 'pending':
                messages.error(request, "Your account is pending approval.")
            elif seller.status == 'rejected':
                messages.error(request, "Your account registration was rejected.")
            elif seller.status == 'blocked':
                messages.error(request, "Your account is blocked. Contact admin.")

        else:
            try:
                seller = SellerProfile.objects.get(user__username=username)
                seller.login_attempts += 1
                if seller.login_attempts >= 3:
                    seller.is_locked = True
                    messages.error(request, "Account locked after 3 failed attempts. Contact admin.")
                else:
                    messages.error(request, "Invalid username or password.")
                seller.save()
            except SellerProfile.DoesNotExist:
                messages.error(request, "Invalid username or password.")

    return render(request, 'saller/seller_login.html')






from django.shortcuts import render, redirect
from django.contrib import messages
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SellerProfile

def unlock_username(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()

        if not username:
            messages.error(request, "Please enter username.")
            return render(request, 'unlock_username.html')

        try:
            seller = SellerProfile.objects.get(user__username=username)

            # ✅ Check seller status
            if seller.status != 'approved':
                messages.error(request, "Seller account is not approved.")
                return render(request, 'unlock_username.html')

            # ✅ Check if account is locked
            if seller.is_locked:
                request.session['unlock_user'] = username
                messages.success(request, "Account is locked. Please answer security questions.")
                return redirect('seller_unlock_questions')
            else:
                messages.info(request, "Your account is already unlocked.")

        except SellerProfile.DoesNotExist:
            messages.error(request, "Seller account not found.")

    return render(request, 'saller/unlock_username.html')




import hashlib
import secrets

from datetime import timedelta


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import SellerProfile, SellerPasswordResetToken
from .forms import (
    SellerForgotPasswordForm,
    SellerResetPasswordForm,
)


@never_cache
def seller_forgot_password(request):

    if request.method == "POST":

        form = SellerForgotPasswordForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"].strip().lower()

            seller = (
                SellerProfile.objects
                .select_related("user")
                .filter(email__iexact=email)
                .first()
            )

            if not seller:

                seller = (
                    SellerProfile.objects
                    .select_related("user")
                    .filter(user__email__iexact=email)
                    .first()
                )

            if not seller:

                messages.error(
                    request,
                    "This email address is not registered with a ShopKart Seller account."
                )

                return redirect(
                    "seller_forgot_password"
                )

            SellerPasswordResetToken.objects.filter(
                seller=seller,
                used=False
            ).update(
                used=True,
                used_at=timezone.now()
            )

            raw_token = secrets.token_urlsafe(64)

            token_hash = hashlib.sha512(
                raw_token.encode("utf-8")
            ).hexdigest()

            expires_at = (
                timezone.now()
                + timedelta(minutes=15)
            )

            SellerPasswordResetToken.objects.create(
                seller=seller,
                token_hash=token_hash,
                expires_at=expires_at,
                used=False
            )

            site_url = getattr(
                settings,
                "SITE_URL",
                "http://127.0.0.1:8000"
            ).rstrip("/")

            reset_url = (
                f"{site_url}"
                f"/seller/password-reset/"
                f"{raw_token}/"
            )

            username = seller.user.username

            subject = "ShopKart Seller Password Reset"

            text_message = f"""
Hello {username},

We received a request to reset your ShopKart Seller account password.

Click the link below to create a new password:

{reset_url}

This link:

- Expires in 15 minutes
- Can be used only once
- Becomes invalid after your password is changed
- Cannot be reused

If you did not request this password reset, please ignore this email.

Regards,
ShopKart Seller Security Team
"""

            html_message = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>ShopKart Password Reset</title>

</head>

<body style="
    margin:0;
    padding:0;
    background:#f4f7fb;
    font-family:Arial,Helvetica,sans-serif;
">

<div style="
    max-width:620px;
    margin:40px auto;
    background:#ffffff;
    border-radius:16px;
    overflow:hidden;
    box-shadow:0 10px 35px rgba(0,0,0,.08);
">

    <div style="
        background:#2563eb;
        color:#ffffff;
        padding:28px;
        text-align:center;
    ">

        <h1 style="margin:0;">
            ShopKart
        </h1>

        <p style="margin:8px 0 0;">
            Seller Account Security
        </p>

    </div>

    <div style="
        padding:35px;
        color:#1f2937;
    ">

        <h2>
            Password Reset Request
        </h2>

        <p>
            Hello <strong>{username}</strong>,
        </p>

        <p>
            We received a request to reset your
            ShopKart Seller account password.
        </p>

        <div style="
            text-align:center;
            margin:30px 0;
        ">

            <a
                href="{reset_url}"
                style="
                    display:inline-block;
                    padding:14px 28px;
                    background:#2563eb;
                    color:#ffffff;
                    text-decoration:none;
                    border-radius:10px;
                    font-weight:bold;
                "
            >
                Reset Password
            </a>

        </div>

        <div style="
            background:#f8fafc;
            border-left:4px solid #2563eb;
            padding:16px;
            border-radius:8px;
        ">

            <strong>Security information</strong>

            <ul>

                <li>
                    Link expires in 15 minutes.
                </li>

                <li>
                    Link can be used only once.
                </li>

                <li>
                    Link becomes invalid after password change.
                </li>

                <li>
                    Do not share this link.
                </li>

            </ul>

        </div>

        <p style="
            margin-top:25px;
            color:#64748b;
            font-size:14px;
        ">

            If you did not request this password reset,
            you can safely ignore this email.

        </p>

    </div>

    <div style="
        padding:20px;
        text-align:center;
        background:#f8fafc;
        color:#64748b;
        font-size:13px;
    ">

        ShopKart Seller Security Team

    </div>

</div>

</body>

</html>
"""

            # =====================================================
            # SEND EMAIL
            # =====================================================

            try:

                email_message = EmailMultiAlternatives(
                    subject=subject,
                    body=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )

                email_message.attach_alternative(
                    html_message,
                    "text/html"
                )

                email_message.send(
                    fail_silently=False
                )

            except Exception:

                messages.error(
                    request,
                    "Unable to send the reset email. Please try again later."
                )

                return redirect(
                    "seller_forgot_password"
                )

            # =====================================================
            # SUCCESS
            # =====================================================

            messages.success(
                request,
                "Your email is registered. A password reset link has been sent to your email."
            )

            return redirect(
                "seller_forgot_password"
            )

    else:

        form = SellerForgotPasswordForm()

    response = render(
        request,
        "saller/seller_forgot_password.html",
        {
            "form": form
        }
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )







from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import transaction
from django.views.decorators.cache import never_cache

from .models import SellerProfile

MAX_IMAGE_SIZE = 5 * 1024 * 1024       # 5 MB
MAX_PDF_SIZE = 10 * 1024 * 1024        # 10 MB


def validate_registration_file(uploaded_file, field_name="document"):

    if not uploaded_file:
        return None


    filename = uploaded_file.name.lower()

    allowed_extensions = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
    }

    extension = None

    for ext in allowed_extensions:
        if filename.endswith(ext):
            extension = ext
            break


    if extension is None:

        raise ValueError(
            f"{field_name}: Only PDF, JPG, JPEG or PNG files are allowed."
        )

    if extension == ".pdf":

        if uploaded_file.size > MAX_PDF_SIZE:

            raise ValueError(
                f"{field_name}: PDF file must be 10 MB or smaller."
            )

    else:

        if uploaded_file.size > MAX_IMAGE_SIZE:

            raise ValueError(
                f"{field_name}: Image must be 5 MB or smaller."
            )


    uploaded_file.seek(0)

    header = uploaded_file.read(16)

    uploaded_file.seek(0)

    if extension == ".pdf":

        if not header.startswith(b"%PDF"):

            raise ValueError(
                f"{field_name}: Invalid PDF file."
            )

    else:

        valid_image = False


        # JPEG
        if header.startswith(b"\xff\xd8\xff"):
            valid_image = True


        # PNG
        elif header.startswith(b"\x89PNG\r\n\x1a\n"):
            valid_image = True


        if not valid_image:

            raise ValueError(
                f"{field_name}: Invalid image file."
            )


    return uploaded_file

@never_cache
def seller_register_step1(request):

    # =====================================================
    # PREVENT REOPENING COMPLETED STEP 1
    # =====================================================

    if request.session.get("seller_step1_completed"):

        seller_id = request.session.get("seller_id")

        if seller_id:

            return redirect(
                "seller_register_step2",
                seller_id=seller_id
            )

        request.session.pop(
            "seller_step1_completed",
            None
        )

        request.session.pop(
            "seller_id",
            None
        )

    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        try:

            # =================================================
            # BUSINESS TYPE VALIDATION
            # =================================================

            business_type = (
                request.POST.get(
                    "business_type",
                    ""
                ).strip().lower()
            )

            allowed_business_types = {
                "individual",
                "proprietorship",
                "partnership",
                "llp",
                "private_limited",
                "opc",
            }

            if business_type not in allowed_business_types:

                raise ValueError(
                    "Please select a valid Business Type."
                )

            # =================================================
            # GET UPLOADED FILES
            # =================================================

            profile_photo = request.FILES.get(
                "profile_photo"
            )

            gst_certificate = request.FILES.get(
                "gst_certificate"
            )

            incorporation_certificate = request.FILES.get(
                "incorporation_certificate"
            )

            partnership_deed = request.FILES.get(
                "partnership_deed"
            )

            trademark_certificate = request.FILES.get(
                "trademark_certificate"
            )

            pan_image = request.FILES.get(
                "pan_image"
            )

            business_license = request.FILES.get(
                "business_license"
            )

            llp_agreement = request.FILES.get(
                "llp_agreement"
            )

            moa_document = request.FILES.get(
                "moa_document"
            )

            aoa_document = request.FILES.get(
                "aoa_document"
            )

            udyam_registration = request.FILES.get(
                "udyam_registration"
            )

            shop_establishment_license = request.FILES.get(
                "shop_establishment_license"
            )

            # =================================================
            # FILE VALIDATION
            # =================================================

            files_to_validate = [

                (
                    profile_photo,
                    "Profile Photo"
                ),

                (
                    gst_certificate,
                    "GST Certificate"
                ),

                (
                    incorporation_certificate,
                    "Incorporation Certificate"
                ),

                (
                    partnership_deed,
                    "Partnership Deed"
                ),

                (
                    trademark_certificate,
                    "Trademark Certificate"
                ),

                (
                    pan_image,
                    "PAN Image"
                ),

                (
                    business_license,
                    "Business License"
                ),

                (
                    llp_agreement,
                    "LLP Agreement"
                ),

                (
                    moa_document,
                    "MOA Document"
                ),

                (
                    aoa_document,
                    "AOA Document"
                ),

                (
                    udyam_registration,
                    "Udyam Registration"
                ),

                (
                    shop_establishment_license,
                    "Shop Establishment License"
                ),
            ]

            for uploaded_file, field_name in files_to_validate:

                if uploaded_file:

                    validate_registration_file(
                        uploaded_file,
                        field_name
                    )

            # =================================================
            # DATABASE TRANSACTION
            # =================================================

            with transaction.atomic():

                # =============================================
                # CREATE USER
                # =============================================

                user = User.objects.create_user(

                    username=request.POST.get(
                        "username"
                    ),

                    email=request.POST.get(
                        "email"
                    ),

                    password=request.POST.get(
                        "password"
                    )
                )

                # =============================================
                # CREATE SELLER PROFILE
                # =============================================

                seller = SellerProfile.objects.create(

                    user=user,

                    business_type=business_type,

                    wedding_anniversary=(
                        request.POST.get(
                            "wedding_anniversary"
                        ) or None
                    ),

                    date_of_birth=(
                        request.POST.get(
                            "date_of_birth"
                        ) or None
                    ),

                    gender=request.POST.get(
                        "gender"
                    ),

                    email=request.POST.get(
                        "email"
                    ),

                    company_name=request.POST.get(
                        "company_name"
                    ),

                    mobile_number=request.POST.get(
                        "mobile"
                    ),

                    address=request.POST.get(
                        "address"
                    ),

                    state=request.POST.get(
                        "state"
                    ),

                    city=request.POST.get(
                        "city"
                    ),

                    pincode=request.POST.get(
                        "pincode"
                    ),

                    country=request.POST.get(
                        "country"
                    ),

                    # =========================================
                    # DOCUMENT UPLOADS
                    # =========================================

                    profile_photo=profile_photo,

                    gst_certificate=gst_certificate,

                    incorporation_certificate=(
                        incorporation_certificate
                    ),

                    partnership_deed=partnership_deed,

                    trademark_certificate=trademark_certificate,

                    brand_authorization_letter=pan_image,

                    business_license=business_license,

                    llp_agreement=llp_agreement,

                    moa_document=moa_document,

                    aoa_document=aoa_document,

                    udyam_registration=udyam_registration,

                    shop_establishment_license=(
                        shop_establishment_license
                    ),
                )

                # =============================================
                # SESSION MANAGEMENT
                # =============================================

                request.session[
                    "seller_step1_completed"
                ] = True

                request.session[
                    "seller_id"
                ] = seller.id

                request.session.modified = True

                # =============================================
                # REDIRECT TO STEP 2
                # =============================================

                return redirect(
                    "seller_register_step2",
                    seller_id=seller.id
                )

        except Exception as e:

            print(
                "Seller Registration Error:",
                str(e)
            )

            return render(
                request,
                "saller/step1.html",
                {
                    "step": 1,
                    "error": str(e)
                }
            )

    # =====================================================
    # GET REQUEST
    # =====================================================

    response = render(
        request,
        "saller/step1.html",
        {
            "step": 1
        }
    )

    # =====================================================
    # PREVENT CACHE
    # =====================================================

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, "
        "max-age=0, private"
    )

    response["Pragma"] = "no-cache"

    response["Expires"] = "0"

    return response


from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from .models import SellerProfile

@never_cache
def seller_register_step2(request, seller_id):

    if not request.session.get("seller_step1_completed"):
        return redirect("seller_register_step1")

    session_seller_id = request.session.get("seller_id")

    if not session_seller_id:
        return redirect("seller_register_step1")


    if int(session_seller_id) != int(seller_id):
        return redirect("seller_register_step1")

    seller = get_object_or_404(
        SellerProfile,
        id=seller_id
    )

    if request.session.get("seller_step2_completed"):

        completed_seller_id = request.session.get(
            "seller_step2_seller_id"
        )

        if completed_seller_id == seller_id:

            return redirect(
                "seller_register_step3",
                seller.id
            )

        return redirect("seller_register_step1")

    if request.method == "POST":

        seller.aadhar_number = request.POST.get(
            "aadhar_number"
        )

        seller.pan_number = request.POST.get(
            "pan_number"
        )

        seller.aadhar_image = request.FILES.get(
            "aadhar_image"
        )

        seller.pan_image = request.FILES.get(
            "pan_image"
        )

        seller.gst_certificate = request.FILES.get(
            "gst_certificate"
        )

        seller.save()

        request.session["seller_step2_completed"] = True

        request.session["seller_step2_seller_id"] = seller.id

        request.session.modified = True

        return redirect(
            "seller_register_step3",
            seller.id
        )

    response = render(
        request,
        "saller/step2.html",
        {
            "step": 2,
            "seller": seller
        }
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, "
        "max-age=0, private"
    )

    response["Pragma"] = "no-cache"

    response["Expires"] = "0"


    return response



from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from .models import SellerProfile

@never_cache
def seller_register_step3(request, seller_id):

 
    if not request.session.get("seller_step2_completed"):
        return redirect("seller_register_step2", seller_id=seller_id)

    session_seller_id = request.session.get("seller_id")

    if not session_seller_id:
        return redirect("seller_register_step1")


    if int(session_seller_id) != int(seller_id):
        return redirect("seller_register_step1")

    seller = get_object_or_404(
        SellerProfile,
        id=seller_id
    )

    if request.session.get("seller_step3_completed"):

        completed_seller_id = request.session.get(
            "seller_step3_seller_id"
        )

        if completed_seller_id == seller.id:

            return redirect(
                "registration_complete"
            )

        return redirect("seller_register_step1")

    if request.method == "POST":

        liveface_scan = request.FILES.get(
            "liveface_scan"
        )

        if liveface_scan:
            seller.liveface_scan = liveface_scan

        seller.latitude = (
            request.POST.get("latitude")
            or None
        )

        seller.longitude = (
            request.POST.get("longitude")
            or None
        )

        seller.live_location = (
            request.POST.get(
                "live_location",
                ""
            ).strip()
        )

        seller.save()

        request.session["seller_step3_completed"] = True

        request.session["seller_step3_seller_id"] = seller.id

        request.session.modified = True

        return redirect(
            "registration_complete"
        )

    response = render(
        request,
        "saller/step3.html",
        {
            "step": 3,
            "seller": seller
        }
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, "
        "max-age=0, private"
    )

    response["Pragma"] = "no-cache"

    response["Expires"] = "0"


    return response

# STEP 4
def registration_completex(request):
    return render(request, "saller/step4.html", {"step": 4})


from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
def registration_complete(request):

    request.session.pop("seller_step1_completed", None)
    request.session.pop("seller_step2_completed", None)
    request.session.pop("seller_step2_seller_id", None)
    request.session.pop("seller_step3_completed", None)
    request.session.pop("seller_step3_seller_id", None)
    request.session.pop("seller_id", None)

    request.session.modified = True

    response = render(
        request,
        "saller/step4.html",
        {
            "step": 4
        }
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, "
        "max-age=0, private"
    )

    response["Pragma"] = "no-cache"
    response["Expires"] = "0"


    return response




from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import (
    F,
    Sum,
    DecimalField,
    ExpressionWrapper,
    Value,
)
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from .models import (
    SellerProfile,
    Product,
    Placedorderxx,
    CustomerRegistration,
    SellerLoginHistory,
)




@login_required
def seller_dashboard(request):

    user = request.user

    seller = SellerProfile.objects.get(user=user)

    seller_username = user.username

    products = Product.objects.filter(
        vendor=seller_username
    )

    total_products = products.count()

    orders = (
        Placedorderxx.objects
        .filter(
            product__vendor=seller_username
        )
        .select_related(
            "user",
            "product"
        )
        .order_by("-id")
    )

    total_orders = orders.count()

    revenue_expression = ExpressionWrapper(
        (
            F("quantity") * F("product__selling_price")
        )
        - Coalesce(
            F("coupon_discount"),
            Value(0.0)
        ),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2
        )
    )

    total_revenue = (
        orders
        .filter(
            status__in=[
                "Delivered",
                "Completed",
                "delivered",
                "completed"
            ]
        )
        .aggregate(
            total=Sum(revenue_expression)
        )["total"] or 0
    )
    if total_revenue < 0:
        total_revenue = 0


    paginator = Paginator(
        orders,
        3
    )

    page_number = request.GET.get("page")

    recent_orders = paginator.get_page(
        page_number
    )

    new_order_time = date.today() - timedelta(
        days=2
    )

    for order in recent_orders:
        product_price = order.product.selling_price or 0

        quantity = order.quantity or 0

        coupon_discount = order.coupon_discount or 0


        gross_amount = (
            quantity * product_price
        )

        net_amount = (
            gross_amount - coupon_discount
        )

        if net_amount < 0:
            net_amount = 0

        order.gross_amount = gross_amount
        order.coupon_discount_amount = coupon_discount
        order.total = int(net_amount)

        order.is_new = (
            order.created_at.date() >= new_order_time
        )

    customers = (
        CustomerRegistration.objects
        .filter(
            user__placedorderxx__product__vendor=seller_username
        )
        .distinct()
    )

    total_customers = customers.count()

    history = (
        SellerLoginHistory.objects
        .filter(
            seller=user
        )
        .order_by(
            "-login_time"
        )
        .first()
    )

    login_time = None
    logout_time = None
    last_login = user.last_login
    spent_hours = ""

    if history:

        login_time = history.login_time

        logout_time = history.logout_time

        if logout_time:

            spent = (
                logout_time - login_time
            )

        else:

            spent = (
                timezone.now() - login_time
            )

        total_seconds = int(
            spent.total_seconds()
        )

        hours = total_seconds // 3600

        minutes = (
            total_seconds % 3600
        ) // 60

        spent_hours = (
            f"{hours} Hour {minutes} Minute"
        )

    context = {

        # Seller
        "seller": seller,

        # Products
        "products": products,

        # Orders
        "recent_orders": recent_orders,
        "orders": orders,

        # Counts
        "total_products": total_products,
        "total_orders": total_orders,
        "total_customers": total_customers,

        # Revenue AFTER coupon discount
        "total_revenue": total_revenue,

        # Date
        "today": date.today(),

        # Login history
        "login_time": login_time,
        "logout_time": logout_time,
        "last_login": last_login,
        "spent_hours": spent_hours,
    }

    return render(
        request,
        "saller/seller_dashboard.html",
        context
    )

@login_required
def saller_product_list(request):
    products = Product.objects.filter(vendor=request.user)

    return render(request, "saller/saller_product_list.html", {
        "products": products
    })




from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .forms import AdvertisementForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum


@login_required
def saller_advertisements(request):

    ads = Advertisementx.objects.filter(
        seller=request.user
    )

    total_ads = ads.count()

    active_ads = ads.filter(
        status="RUNNING"
    ).count()

    pending_ads = ads.filter(
        status="WAITING_APPROVAL"
    ).count()

    expired_ads = ads.filter(
        status="EXPIRED"
    ).count()

    total_spending = ads.aggregate(
        total=Sum("amount")
    )["total"] or 0

    context = {

        "total_ads": total_ads,
        "active_ads": active_ads,
        "pending_ads": pending_ads,
        "expired_ads": expired_ads,
        "total_spending": total_spending,
        "ads": ads

    }

    return render(
        request,
        "saller/advertisements.html",
        context
    )



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Placedorderxx

@login_required
def saller_customer_orders(request):
    # ✅ Filter orders by snapshot vendor field
    orders = Placedorderxx.objects.filter(vendor=request.user.username).select_related("user")

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")

        try:
            order = Placedorderxx.objects.get(id=order_id)

            # ✅ Only allow seller to update their own orders
            if order.vendor != request.user.username:
                return redirect("saller_customer_orders")

        except Placedorderxx.DoesNotExist:
            return redirect("saller_customer_orders")

        # Prevent admin-locked orders
        if order.updated_by_admin:
            return redirect("saller_customer_orders")

        # ✅ Update order status safely
        order.status = status
        order.save()

    return render(request, "saller/saller_customer_orders.html", {"orders": orders})



def seller_neworders(request):
    """
    Display all orders for the logged-in seller's products.
    """
    seller_username = request.user.username
    orders = Placedorderxx.objects.filter(product__vendor=seller_username).select_related('product', 'user')

    return render(request, 'saller/seller_neworders.html', {'orders': orders})

@login_required
def seller_order_status(request):
    seller_name = request.user.username

    orders = Placedorderxx.objects.filter(
        product__vendor=seller_name
    )

    status_counts = orders.values("status").annotate(
        total=Count("status")
    )

    data = {
        "pending": 0,
        "processing": 0,
        "shipped": 0,
        "delivered": 0,
        "completed": 0,
    }

    for item in status_counts:
        status = (item["status"] or "").lower()

        if status in data:
            data[status] = item["total"]

    context = {
        "labels": list(data.keys()),
        "values": list(data.values()),
    }

    return render(
        request,
        "saller/seller_order_status.html",
        context,
    )



from datetime import timedelta
from decimal import Decimal

from django.db.models import F, Sum, DecimalField, ExpressionWrapper, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils.timezone import now

from .models import Placedorderxx


@login_required
def saller_sales_report(request):
    today = timezone.localdate()

    # Calendar reporting periods.
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    # Completed orders for the logged-in seller only.
    seller_filter = {
        "product__vendor": request.user.username,
        "status__iexact": "completed",
    }

    def get_sales(start_date, end_date):
        return list(
            Placedorderxx.objects.filter(
                **seller_filter,
                ordered_date__date__gte=start_date,
                ordered_date__date__lte=end_date,
            )
            .select_related("product")
            .order_by("-ordered_date")
        )

    # Fetch orders for each period.
    daily_sales = get_sales(today, today)
    weekly_sales = get_sales(week_start, today)
    monthly_sales = get_sales(month_start, today)
    yearly_sales = get_sales(year_start, today)

    def calculate_sales(orders):
        total_quantity = 0
        total_selling_price = ZERO
        total_coupon_discount = ZERO
        total_final_amount = ZERO

        for order in orders:
            quantity = max(int(order.quantity or 0), 0)
            product = order.product

            # Unit selling price and total before discount.
            unit_price = money(product.selling_price)
            selling_price_total = money(unit_price * quantity)

            # First use the discount saved on the order.
            saved_discount = getattr(order, "coupon_discount", None)

            if (
                saved_discount is not None
                and money(saved_discount) > ZERO
            ):
                coupon_discount_total = money(saved_discount)

            else:
                # Fallback to the product coupon discount.
                # Adjust these field names if your Product model
                # uses different names.
                product_discount = money(
                    getattr(product, "coupon_discount", 0)
                )

                coupon_active = getattr(
                    product, "coupon_active", True
                )
                coupon_expiry = getattr(
                    product, "coupon_expiry", None
                )

                coupon_valid = (
                    coupon_active
                    and (
                        coupon_expiry is None
                        or coupon_expiry >= today
                    )
                )

                if coupon_valid:
                    coupon_discount_total = money(
                        product_discount * quantity
                    )
                else:
                    coupon_discount_total = ZERO

            # Keep discount within the selling-price amount.
            coupon_discount_total = min(
                max(coupon_discount_total, ZERO),
                selling_price_total,
            )

            # Final total after discount.
            final_total = money(
                selling_price_total - coupon_discount_total
            )

            # IMPORTANT: names used by your HTML template.
            order.selling_price_unit = unit_price
            order.selling_price_total = selling_price_total
            order.coupon_discount_total = coupon_discount_total

            # Your HTML uses order.total_amount.
            order.total_amount = final_total

            # Keep this alias if another template uses it.
            order.final_total = final_total

            total_quantity += quantity
            total_selling_price += selling_price_total
            total_coupon_discount += coupon_discount_total
            total_final_amount += final_total

        return {
            "total_quantity": total_quantity,
            "selling_price": money(total_selling_price),
            "coupon_discount": money(total_coupon_discount),
            "revenue": money(total_final_amount),
        }

    # Calculate totals for each reporting period.
    daily_totals = calculate_sales(daily_sales)
    weekly_totals = calculate_sales(weekly_sales)
    monthly_totals = calculate_sales(monthly_sales)
    yearly_totals = calculate_sales(yearly_sales)

    context = {
        # Order lists.
        "daily_sales": daily_sales,
        "weekly_sales": weekly_sales,
        "monthly_sales": monthly_sales,
        "yearly_sales": yearly_sales,

        # Quantities.
        "daily_total_quantity": daily_totals["total_quantity"],
        "weekly_total_quantity": weekly_totals["total_quantity"],
        "monthly_total_quantity": monthly_totals["total_quantity"],
        "yearly_total_quantity": yearly_totals["total_quantity"],

        # Selling price before discounts.
        "daily_selling_price": daily_totals["selling_price"],
        "weekly_selling_price": weekly_totals["selling_price"],
        "monthly_selling_price": monthly_totals["selling_price"],
        "yearly_selling_price": yearly_totals["selling_price"],

        # Coupon discounts.
        "daily_coupon_discount": daily_totals["coupon_discount"],
        "weekly_coupon_discount": weekly_totals["coupon_discount"],
        "monthly_coupon_discount": monthly_totals["coupon_discount"],
        "yearly_coupon_discount": yearly_totals["coupon_discount"],

        # Final amount after discounts.
        "daily_revenue": daily_totals["revenue"],
        "weekly_revenue": weekly_totals["revenue"],
        "monthly_revenue": monthly_totals["revenue"],
        "yearly_revenue": yearly_totals["revenue"],

        # IMPORTANT: variable names required by your HTML.
        "daily_total_amount": daily_totals["revenue"],
        "weekly_total_amount": weekly_totals["revenue"],
        "monthly_total_amount": monthly_totals["revenue"],
        "yearly_total_amount": yearly_totals["revenue"],
    }

    return render(
        request,
        "saller/saller_sales_report.html",
        context,
    )





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Placedorderxx

@login_required
def seller_top_selling_products(request):
    seller_name = request.user.username

    # Only completed / delivered orders (real sales)
    orders = (
        Placedorderxx.objects
        .filter(
            product__vendor=seller_name,
            status__in=['delivered', 'completed']
        )
        .values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]  # Top 5 products
    )

    labels = [item['product__name'] for item in orders]
    values = [item['total_sold'] for item in orders]

    context = {
        'labels': labels,
        'values': values,
    }

    return render(request, 'saller/seller_top_selling_products.html', context)




from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product, Placedorderxx


def saller_low_stock(request):
    """
    Display all products with quantity less than 5 for the logged-in seller.
    """
    seller_username = request.user.username  # Assuming vendor stores username
    products = Product.objects.filter(vendor=seller_username, quantity__lt=5)
    return render(request, 'saller/saller_low_stock.html', {'products': products})




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import ReturnRequested
@login_required
def seller_return_list(request):


    returns = ReturnRequested.objects.filter(
        vendor=request.user.username
    ).order_by(
        "-requested_at"
    )


    return render(
        request,
        "seller_return_list.html",
        {
            "returns":returns
        }
    )


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Tickets
from django.contrib.auth.models import User
import uuid

# ---------- Helper ----------
def generate_ticket_number():
    return f"TCK-{uuid.uuid4().hex[:8].upper()}"


# ---------- Seller Dashboard ----------
@login_required
def seller_ticket_dashboard(request):
    tickets = Tickets.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'saller/seller_ticket_dashboard.html', {'tickets': tickets})

