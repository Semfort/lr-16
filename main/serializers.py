from rest_framework import serializers
from .models import Product, ProductCategory, Manufacturer, Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий товаров"""
    class Meta:
        model = ProductCategory
        fields = '__all__'  # Включает все поля модели


class ManufacturerSerializer(serializers.ModelSerializer):
    """Сериализатор для производителей"""
    class Meta:
        model = Manufacturer
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для товаров"""
    category_name = serializers.ReadOnlyField(source='category.name')
    manufacturer_name = serializers.ReadOnlyField(source='manufacturer.name')

    class Meta:
        model = Product
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    """Сериализатор для элементов внутри корзины"""
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_id', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для самой корзины"""
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at']