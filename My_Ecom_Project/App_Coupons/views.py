from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from django.views.generic import View
from App_Coupons.models import Coupons
from App_Coupons.forms import CouponApplyForm
from App_Order.models import Order

# Create your views here.
@login_required
def get_coupon(request, code):
    try:
        coupon = Coupons.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("App_Payment:checkout")

@login_required
def add_coupon(request):
    if request.method == 'GET':
        couponf = True
        cform = CouponApplyForm(request.GET)
        if cform.is_valid():
            try:
                code = cform.cleaned_data.get('code')
                order = Order.objects.get(user=request.user, ordered=False)
                order.coupon = get_coupon(request, code)
                order.save()
                messages.success(request, "Successfully added coupon")
                return render(request, 'App_Coupons/coupon.html')
            except ObjectDoesNotExist:
                messages.info(request, "This is not valid coupon")
                return redirect("App_Coupons:add_coupon")
    return render(request, 'App_Coupons/coupon.html', context={'cform':cform, 'couponf':couponf})
