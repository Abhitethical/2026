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
    








































































def productsearch(request):
    return render(request,"productsearch.html")


def forgotpassword(request):
    return render(request,"forgotpassword.html")

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
    




