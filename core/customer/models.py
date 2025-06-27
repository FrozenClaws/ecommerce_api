from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _ 
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, timedelta

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Provide a valid email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()


    def __str__(self):
        return self.email
    
class Product(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=True, default="")
    description = models.TextField(max_length=500, blank=True, default="")
    actual_price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    stock = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, default=None)

class CartItem(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=True, default=1)
    coupon = models.CharField(max_length=50, blank=True, default="")
    rate = models.DecimalField(max_digits=20, decimal_places=2, default=00.00)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=00.00)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, default=None)

class Discounts(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    discount = models.IntegerField(validators=[
            MinValueValidator(0, message="Discount cannot be negative."),
            MaxValueValidator(100, message="Discount cannot exceed 100.")
        ], default=0)
    provider = models.CharField(max_length=100, default="")
    coupon_code = models.CharField(max_length=50, unique=True, default="")
    allowed_users = models.IntegerField(validators=[
            MinValueValidator(0, message="Users cannot be negative."),
        ], default=0)
    used = models.IntegerField(validators=[
            MinValueValidator(0, message="Users cannot be negative."),
        ], default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, default=None)
    expiry = models.DateTimeField(default=datetime.now() + timedelta(days=10))
        
class Image(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/')
    



    
        
