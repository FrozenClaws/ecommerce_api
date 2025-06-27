from rest_framework import serializers
from .models import CustomUser, Product, CartItem, Discounts
from django.utils import timezone
from django.db.utils import IntegrityError
from decimal import Decimal

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "username", "email", "password"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class ProductSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=20, decimal_places=2, default=00.00)
    stock = serializers.IntegerField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()

    def validate(self, attrs):
        if(attrs['stock'] < 0):
            raise serializers.ValidationError("Bad Value")
        return attrs
    
    def create(self, validated_data):
        product = Product.objects.create(**validated_data)
        return product
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.stock= validated_data.get('stock', instance.stock)
        instance.description = validated_data.get('description', instance.description)
        for item in CartItem.objects.all():
            item.rate = instance.price
            item.total = item.rate*item.quantity
            item.save()
        instance.updated_at = timezone.now()
        instance.save()
        return instance



class CustomUserSerializer(serializers.ModelSerializer):
    model = CustomUser
    fields = "__all__"
    

class CartItemSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    user = serializers.ReadOnlyField
    product = serializers.SlugRelatedField(queryset=Product.objects.all(), slug_field='id')
    coupon = serializers.CharField()
    quantity = serializers.IntegerField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    rate = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()

    def validate(self, attrs):

        # Negative value for quantity (It can be added in model itself (MinValueValidator))

        if(attrs['quantity'] < 0):
            raise serializers.ValidationError("Bad value")
        
        # Product id validation

        try:
            Product.objects.get(id=attrs['product'].id)
        except(Product.DoesNotExist):
            raise serializers.ValidationError("There's no such product in the store")
        
        # Stock and Requested Quantity check

        try:
            item = CartItem.objects.get(product=attrs['product'], user=self.context['request'].user)
        except(CartItem.DoesNotExist):
            if(attrs['quantity'] > attrs['product'].stock):
                raise serializers.ValidationError(f"Currently there's only {attrs['product'].stock} remaining in the stock")
            return attrs 
        
        # Discount Validation

        try:
            discounts = Discounts.objects.filter(product=attrs['product'])
        except(Discounts.DoesNotExist):
            return attrs
        for dis in discounts.values():
            if(dis["coupon_code"] == attrs["coupon"]):
                if(dis["expiry"] <= timezone.now() or dis["used"] >= dis["allowed_users"]):
                    raise serializers.ValidationError("Coupon code expired or reached its limit!")
                return attrs
        raise serializers.ValidationError("Invalid Coupon Code!")


    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        try:
            item = CartItem.objects.get(user=validated_data['user'], product=validated_data['product'])
        except(CartItem.DoesNotExist):

            # Incrementing used count for discount

            dis = Discounts.objects.get(product=validated_data['product'], coupon_code=validated_data["coupon"])
            dis.used += 1
            dis.save()

            # Adding discounted value to the requested product

            prod = Product.objects.get(name=validated_data.get('product').name)
            validated_data['rate'] = prod.price - prod.price*Decimal(dis.discount/100)
            validated_data['total'] = validated_data['rate'] * validated_data['quantity']
            item = CartItem.objects.create(**validated_data)
            return item
        
        raise serializers.ValidationError("Item already exists in the cart")
        
    
    def update(self, instance, validated_data):
        instance.product = validated_data.get('product', instance.product)
        instance.quantity = validated_data.get('quantity', instance.quantity)

        # Updating discount
        item = Product.objects.get(name=instance.product.name)
        dis = Discounts.objects.get(product=validated_data['product'], coupon_code=validated_data["coupon"])
        instance.rate = item.price - item.price*Decimal(dis.discount/100)
        instance.total = instance.rate * validated_data['quantity']
        instance.updated_at = timezone.now()
        instance.save()
        return instance
    
class DiscountSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    product = serializers.SlugRelatedField(queryset=Product.objects.all(), slug_field="id")
    discount = serializers.IntegerField()
    provider = serializers.CharField()
    coupon_code = serializers.CharField()
    allowed_users = serializers.IntegerField()
    used = serializers.ReadOnlyField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    expiry = serializers.DateTimeField()

    def create(self, validated_data):
        validated_data['used'] = 0
        dis = Discounts.objects.create(**validated_data)
        return dis
    
    def update(self, instance, validated_data):
        instance.product = validated_data.get('product', instance.product)
        instance.provider = validated_data.get('provider', instance.provider)
        instance.coupon_code = validated_data.get('coupon_code', instance.coupon_code)

        # Changing the rate for already saved items in cart with respect to the change in discount value
        if instance.discount != validated_data['discount']: # Efficient! Not happens everytime
            instance.discount = validated_data.get('discount', instance.discount)
            for item in CartItem.objects.filter(product=instance.product, coupon=instance.coupon_code).values():
                item['rate'] = instance.product.price - item.price*Decimal(instance.discount/100)
                item['total'] = item['rate'] * item['quantity']

        instance.allowed_users = validated_data.get('allowed_users', instance.allowed_users)
        instance.expiry = validated_data.get('expiry', instance.expiry)
        instance.updated_at = timezone.now()
        instance.save()
        return instance
    








