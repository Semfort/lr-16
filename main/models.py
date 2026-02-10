from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Product_category(models.Model):
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
        Product_category,
        on_delete=models.CASCADE,
        verbose_name = "Категория",
        related_name = "products"
    )
    manufacture = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        verbose_name = "Производитель",
        related_name = "products"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

