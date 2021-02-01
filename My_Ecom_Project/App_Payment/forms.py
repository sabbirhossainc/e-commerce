from django import forms
from App_Payment.models import BillingAddress

# forms

class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = ['address', 'zipcode', 'city', 'country']
