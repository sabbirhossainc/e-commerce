from django.urls import path
from App_Coupons import views

app_name = 'App_Coupons'

urlpatterns = [
	path('add-coupon/', views.add_coupon, name='add_coupon'),
]
