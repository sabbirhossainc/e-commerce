from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist


# models and forms
from App_Coupons.models import Coupons
from App_Coupons.forms import CouponApplyForm
from App_Order.models import Order, Cart
from App_Payment.models import BillingAddress
from App_Payment.forms import BillingForm

from django.contrib.auth.decorators import login_required

# for Payment
import requests
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
import socket
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@login_required
def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)[0]
    form = BillingForm(instance=saved_address)
    if request.method == "POST":
        form = BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            form = BillingForm(instance=saved_address)
            messages.success(request, f'Shipping Address Saved!')
    order_qs = Order.objects.filter(user=request.user, ordered=False)[0]
    order_items = order_qs.orderitems.all()
    order_total = order_qs.get_totals()
    order = Order.objects.get(user=request.user, ordered=False)
    coupon = Coupons.objects.all().values_list('code','code')
    promo = order.coupon

    return render(request, 'App_Payment/checkout.html', context={'form':form,'promo':promo,
    'order_items':order_items, 'order_total':order_total,
    'saved_address':saved_address})

@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)[0]
    if not saved_address.is_fully_filled():
        messages.info(request, f'Please complete Shipping Address!')
        return redirect('App_Payment:checkout')

    if not request.user.profile.is_fully_filled():
        messages.info(request, f'Please complete profile details!')
        return redirect('App_Login:profile')

    store_id = 'abc5fb42908a1cd1'
    API_key = 'abc5fb42908a1cd1@ssl'

    mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=store_id,
    sslc_store_pass=API_key)

    status_url = request.build_absolute_uri(reverse('App_Payment:complete'))

    mypayment.set_urls(success_url=status_url, fail_url=status_url,
    cancel_url=status_url, ipn_url=status_url)

    order_qs = Order.objects.filter(user=request.user, ordered=False)[0]
    order_items = order_qs.orderitems.all()
    order_items_count = order_qs.orderitems.count()
    order_total = order_qs.get_totals()

    mypayment.set_product_integration(total_amount=Decimal(order_total), currency='BDT',
    product_category='Mixed', product_name=order_items, num_of_item=order_items_count,
    shipping_method='Courier', product_profile='None')

    current_user = request.user
    user_info = current_user.profile

    mypayment.set_customer_info(name=user_info.full_name, email=current_user.email,
    address1=user_info.address_1, address2=user_info.address_1, city=user_info.city,
    postcode=user_info.zipcode, country=user_info.country, phone=user_info.phone)

    mypayment.set_shipping_info(shipping_to=user_info.full_name, address=saved_address.address,
    city=saved_address.city, postcode=saved_address.zipcode, country=saved_address.country)

    response_data = mypayment.init_payment()
    # print(response_data)
    # return render(request, 'App_Payment/payment.html', context={})
    return redirect(response_data['GatewayPageURL'])

@csrf_exempt
def complete(request):
    if request.method == "POST" or request.method == "post":
        payment_data = request.POST
        status = payment_data['status']

        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            # bank_tran_id = payment_data['bank_tran_id']
            messages.success(request, f'Your Payment Completed Successfully! \
            Page will be redirected in 5 sec.')
            return HttpResponseRedirect(reverse('App_Payment:purchase',
            kwargs={'val_id':val_id, 'tran_id':tran_id,}))

        elif status == 'FAILED':
            messages.warning(request, f'Your Payment FAILED! Please Try Again! \
            Page will be redirected in 5 sec.')

    return render(request, 'App_Payment/complete.html', context={})

@login_required
def purchase(request, val_id, tran_id):
    order = Order.objects.filter(user=request.user, ordered=False)[0]
    orderId = tran_id
    order.ordered = True
    order.orderId = orderId
    order.paymentId = val_id
    order.save()
    cart_items = Cart.objects.filter(user=request.user, purchased=False)
    for item in cart_items:
        item.purchased =True
        item.save()
    return HttpResponseRedirect(reverse('App_Shop:home'))

@login_required
def order_view(request):
    try:
        orders = Order.objects.filter(user=request.user, ordered=True)
        context = {'orders':orders}
    except:
        messages.warning(request, 'You do not have an any active order')
        return redirect('App_Shop:home')
    return render(request, 'App_Payment/order.html', context)
