from django.contrib import admin
from App_Coupons.models import Coupons

# Admin View for Coupons
class CouponsAdmin(admin.ModelAdmin):

	list_display = ('code','valid_form','valid_to','discount','active',)
	list_filter = ('active','valid_form','valid_to',)
	search_fields = ('code',)

admin.site.register(Coupons, CouponsAdmin)
