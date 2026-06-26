import openpyxl
from io import BytesIO
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required  
from .models import Product, CartItem, ProductCategory, Manufacturer, Cart, Order, OrderItem    
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import ExtendedUserCreationForm

# Create your views here.
def index(request):
    return HttpResponse("<h1><a href='http://127.0.0.1:8000/author/'>Великий творец сайта</a>  <a href='http://127.0.0.1:8000/catalog/'>Страница магазина</a></h1>")

def catalog(request):
    return HttpResponse("<h1>Магазин спортивных товаров</h1>")

def author(request):
    return HttpResponse("<h1>Автор: Лоел Семён 89ТП</h1>")

@login_required(login_url='/register/')
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_items = CartItem.objects.filter(cart=cart)
    
    total_cost = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_cost': total_cost,   
    }
    
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
    
    cart, cart_created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,  
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart_view')

@login_required(login_url='/register/')
def update_cart(request, item_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if request.method == 'POST':
        try:
            new_quantity = int(request.POST.get('quantity'))
        except (ValueError, TypeError):
            messages.error(request, "Некорректное число")
            return redirect('cart_view')

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

    return redirect('cart_view')

@login_required(login_url='/register/')
def remove_from_cart(request, pk):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item = get_object_or_404(CartItem, id=pk, cart=cart)
    cart_item.delete()
    return redirect('cart_view')

def register(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('product_list')
    else:
        form = ExtendedUserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})

@login_required(login_url='/register/')
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    if not cart_items.exists():
        messages.error(request, "Ваша корзина пуста. Нечего оформлять!")
        return redirect('cart_view')
    
    total_cost = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(user=request.user, total_cost=total_cost)
    
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
        item.product.quantity_in_stock -= item.quantity
        item.product.save()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Чек Заказа {order.id}"
    
    # Заголовки таблицы Excel
    ws.append([f"Чек по заказу №{order.id}", "", "", ""])
    ws.append([f"Покупатель: {request.user.username}", "", "", ""])
    ws.append(["Товар", "Цена за шт.", "Количество", "Итого"])
    
    for item in order.items.all():
        row_total = item.price * item.quantity
        ws.append([item.product.name, item.price, item.quantity, row_total])
        
    ws.append(["", "", "ОБЩАЯ СУММА:", total_cost])
    
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    subject = f"Ваш заказ №{order.id} успешно оформлен!"
    body = f"Здравствуйте, {request.user.username}!\n\nБлагодарим за покупку. Ваш чек находится во вложении к этому письму."

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=None, 
        to=[request.user.email]
    )

    email.attach(
        f"invoice_order_{order.id}.xlsx", 
        excel_file.read(), 
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    try:
        email.send()
    except Exception as e:
        messages.warning(request, "Заказ оформлен, но письмо не отправлено.")
    
    cart_items.delete()
    
    context = {
        'order': order,
        'total_cost': total_cost
    }
    return render(request, 'shop/success.html', context)
