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
from rest_framework import viewsets, permissions
from rest_framework.response import Response
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .serializers import (
    CategorySerializer, 
    ManufacturerSerializer, 
    ProductSerializer, 
    CartSerializer, 
    CartItemSerializer
)
class CategoryViewSet(viewsets.ModelViewSet):
    """API для управления категориями (CRUD)"""
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ManufacturerViewSet(viewsets.ModelViewSet):
    """API для управления производителями (CRUD)"""
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    """API для управления товарами (CRUD)"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class CartViewSet(viewsets.ModelViewSet):
    """API для управления корзиной пользователя"""
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    """API для добавления, изменения и удаления товаров в корзине"""
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

def api_products(request):
    category_id = request.GET.get('category')
    manufacturer_id = request.GET.get('manufacturer')
    search = request.GET.get('search', '').strip()

    products = Product.objects.all()
    if category_id:
        products = products.filter(category__id=category_id)
    if manufacturer_id:
        products = products.filter(manufacture__id=manufacturer_id)
    if search:
        products = products.filter(name__icontains=search)

    data = []
    for p in products:
        data.append({
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'category': p.category.name if p.category else '',
            'image': p.image.url if p.image else None,
            'quantity_in_stock': p.quantity_in_stock,
            'detail_url': f'/catalog/{p.id}/',
            'add_to_cart_url': f'/cart/add/{p.id}/',
        })
    return JsonResponse({'products': data})




# Create your views here.
@require_POST
@login_required(login_url='/accounts/login/')
def api_add_to_cart(request):
    try:
        body = json.loads(request.body)
        product_id = body.get('product_id')
        product = Product.objects.get(id=product_id)

        if product.quantity_in_stock == 0:
            return JsonResponse({'success': False, 'message': 'Товар отсутствует на складе'}, status=400)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if cart_item.quantity < product.quantity_in_stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                return JsonResponse({'success': False, 'message': 'Достигнуто максимальное количество'}, status=400)

        return JsonResponse({'success': True, 'message': f'«{product.name}» добавлен в корзину!'})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Товар не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)

def index(request):
    products = Product.objects.order_by('-id')[:6]  # последние 6 товаров
    categories = ProductCategory.objects.all()
    return render(request, 'shop/index.html', {
        'products': products,
        'categories': categories,
    })

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
    categories = ProductCategory.objects.all()
    manufacturers = Manufacturer.objects.all()

    category_id = request.GET.get('category')
    manufacturer_id = request.GET.get('manufacturer')
    search = request.GET.get('search', '').strip()

    if category_id:
        products = products.filter(category__id=category_id)
    if manufacturer_id:
        products = products.filter(manufacture__id=manufacturer_id)
    if search:
        products = products.filter(name__icontains=search)

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/catalog.html', {
        'page_obj': page_obj,
        'categories': categories,
        'manufacturers': manufacturers,
        'selected_category': category_id,
        'selected_manufacturer': manufacturer_id,
        'search': search,
    })

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
