from django.shortcuts import render

# IMport views
from django.views.generic import ListView, DetailView

# MOdels
from App_Shop.models import Product, Category

# mixin
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class Home(ListView):
    model = Product
    template_name = 'App_Shop/home.html'

    def get_context_data(self, *args, **kwargs):
        cat_menu = Category.objects.all()
        context = super(Home, self).get_context_data(*args, **kwargs)
        context["cat_menu"] = cat_menu
        return context

def CategoryView(request, id):
    # Categories = Category.objects.all().values_list('title','title')
    products = Product.objects.filter(category=id)
    
    return render(request, 'App_Shop/category.html', {'id':id, 'products':products})

class ProductDetail(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'App_Shop/product_detail.html'

    def get_context_data(self, *args, **kwargs):
        cat_menu = Category.objects.all()
        context = super(ProductDetail, self).get_context_data(*args, **kwargs)
        context["cat_menu"] = cat_menu
        return context
