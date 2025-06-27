from knox import views as knox_views
from django.urls import path, include
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import *

schema_view = get_schema_view(
   openapi.Info(
      title="EcommerceAPI",
      default_version='v1',
      description="An API for facilatiting products and individual user cart management",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
     path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
     path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
     path('register/', UserRegisterView.as_view(), name='register'),
     path(r'login/', LoginView.as_view(), name='knox_login'),
     path(r'logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
     path(r'logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
     path('products/create', ProductCreateView.as_view(), name='product_create'),
     path('products/', ProductListView.as_view(), name='product_list'),
     path('products/<int:pk>', ProductRetrieveView.as_view(), name='product_retrieve'),
     path('products/update/<int:pk>', ProductUpdateView.as_view(), name='product_update'),
     path('products/delete/<int:pk>', ProductDeleteView.as_view(), name='product_delete'),
     path('cart/add', CartAddView.as_view(), name='cart_add'),
     path('cart/', CartListView.as_view(), name='cart_list'),
     path('cart/<int:pk>', CartRetrieveView.as_view(), name='cart_retrieve'),
     path('cart/update/<int:pk>', CartUpdateView.as_view(), name='cart_update'),
     path('cart/delete/<int:pk>', CartDeleteView.as_view(), name='cart_delete'),
     path('cart/buy/<int:pk>', CartBuyView.as_view(), name='cart_buy'),
     path('discount/', DiscountListView.as_view(), name="discount_view"),
     path('discount/create', DiscountCreateView.as_view(), name="discount_create"),
     path('discount/update/<int:pk>', DiscountUpdateView.as_view(), name="discount_update"),
     path('discount/retrieve/<int:pk>', DiscountRetrieveView.as_view(), name="discount_retrieve"),
     path('discount/delete/<int:pk>', DiscountDeleteView.as_view(), name="discount_delete"),
     path('discount/product/<int:pk>', DiscountProductSpecificView.as_view(), name="discount_product"),
]