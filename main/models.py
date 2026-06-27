from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class ProductCategory(models.Model):
    name = models.CharField(
        max_length = 50,
        verbose_name = "Название категории"
    )   
    description = models.TextField(
        blank = True,
        verbose_name = "Описание категории"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Manufacturer(models.Model):
    name = models.CharField(
        max_length = 50,
        verbose_name = "Название производителя"
    )
    country = models.CharField(
        max_length = 50,
        verbose_name = "Страна"
    )
    description = models.TextField(
        blank = True,
        verbose_name = "Описание производителя"
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"


class Product(models.Model):
    name = models.CharField(
        max_length = 50,
        verbose_name = "Название товара"
    )
    description = models.TextField(
        blank = True,
        verbose_name = "Описание товара"
    )
    image = models.ImageField(
        upload_to = "products/",
        verbose_name = "Фото товара",
        blank = True,
        null = True
    )
    price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        verbose_name = "Цена",
        validators=[MinValueValidator(0)]
    )
    quantity_in_stock = models.IntegerField(
        verbose_name = "Количество на складе",
        validators=[MinValueValidator(0)]
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        verbose_name = "Категория",
        related_name = "category_products"
    )
    manufacture = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        verbose_name = "Производитель",
        related_name = "manufacture_products"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name = "Пользователь"
    )
    created_date = models.DateTimeField(
        auto_now_add = True,
        verbose_name = "Дата создания"
    )

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    def total_cost(self):
        return sum(item.item_cost() for item in self.items.all())

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        verbose_name = "Корзина",
        related_name = "items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name = "Продукты",
        related_name = "cart_item"
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Количество"
    )
    def clean(self):
        super().clean()
        if self.product and self.quantity > self.product.quantity_in_stock:
            raise ValidationError(f"Доступно только {self.product.quantity_in_stock} товара")

    def __str__(self):
        return f"{self.product.name} {self.quantity}"
    
    def item_cost(self):
        return self.product.price * self.quantity
    
    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

class Profile(models.Model):
    CUSTOMER = 'customer'
    MANAGER = 'manager'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (CUSTOMER, 'Покупатель'),
        (MANAGER, 'Менеджер'),
        (ADMIN, 'Администратор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    full_name = models.CharField(max_length=100, blank=True, verbose_name='Полное имя')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адрес доставки')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == self.ADMIN

    def is_manager(self):
        return self.role == self.MANAGER

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Покупатель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачен")

    def __str__(self):
        return f"Заказ №{self.id} — {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"