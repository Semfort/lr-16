from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required


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

    @login_required
    def cart_view(request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_items = cart.items.select_related('product').all()
    
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'total_cost': cart.total_cost(),
        }
        
        return render(request, 'main/cart.html', context)