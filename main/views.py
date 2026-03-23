from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required  
from .models import Product, CartItem, ProductCategory, Manufacturer
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Create your views here.
def index(request):
    return HttpResponse("<h1><a href='http://127.0.0.1:8000/author/'>Великий творец сайта</a>  <a href='http://127.0.0.1:8000/catalog/'>Страница магазина</a></h1>")

def catalog(request):
    return HttpResponse("<h1>Магазин спортивных товаров</h1>")

def author(request):
    return HttpResponse("<h1>Автор: Лоел Семён 89ТП</h1>")

def cart(request):
    return render(request, 'shop/cart.html', context)

def product_list(request):
    products = Product.objects.all()

    category_id = request.GET.get('category')
    manufacture_id = request.GET.get('manufacture')
    search_query = request.GET.get('search')

    if category_id:
        products = products.filter(category_id=category_id)

    if manufacture_id:
        products = products.filter(manufacture_id=manufacture_id)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    categories = ProductCategory.objects.all()
    manufacturers = Manufacturer.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers,
    }
    
    return render(request, 'shop/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    context = {
        'product': product
    }
    
    return render(request, 'shop/product_detail.html', context)

@login_required(login_url='/register/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, 
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart')

def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if request.method == 'POST':
        try:
            new_quantity = int(request.POST.get('quantity'))
        except (ValueError, TypeError):
            messages.error(request, "Некорректное число")
            return redirect('cart')

        if new_quantity > cart_item.product.quantity_in_stock:
            messages.error(
                request, 
                f"Ошибка: Доступно только {cart_item.product.quantity_in_stock} шт."
            )
        elif new_quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = new_quantity
            cart_item.save()

    return redirect('cart')

@login_required(login_url='/register/')
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    cart_item = get_object_or_404(CartItem, id=pk, user=request.user)
    if not created:
        cart_item.quantity = 0
        cart_item.save()
    
    cart_item.delete()
    
    return redirect('cart')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('catalog')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})