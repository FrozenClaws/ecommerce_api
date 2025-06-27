from django.contrib.auth import login

from rest_framework import generics
from rest_framework import permissions
from .models import Product, CartItem, CustomUser, Discounts
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer, UserRegisterSerializer, CartItemSerializer, DiscountSerializer
from rest_framework.renderers import MultiPartRenderer


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)
    
class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny, )

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

class ProductRetrieveView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def destroy(self, request, *args, **kwargs):
        item = Product.objects.get(pk=kwargs['pk'])
        item.delete()
        return Response({"message":"Item deleted from the store successfully!"}, status=status.HTTP_200_OK)

class CartAddView(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response({"message": "Added to the cart!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors)
    
class CartListView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

class CartRetrieveView(generics.RetrieveAPIView):
    serializer_class = CartItemSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

class CartUpdateView(generics.UpdateAPIView):
    serializer_class = CartItemSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

class CartDeleteView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        item = CartItem.objects.get(pk=kwargs['pk'])
        item.delete()
        return Response({"message":"Item deleted from the cart successfully!"}, status=status.HTTP_200_OK)
    
class CartBuyView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        item = CartItem.objects.get(pk=kwargs['pk'])
        change = Product.objects.get(id=item.product.id)
        discount = Discounts.objects.get(product=item.product, coupon_code=item.coupon)
        discount.used += 1
        change.stock -= item.quantity
        discount.save()
        change.save()
        item.delete()
        return Response({"message":"Item bought successfully!"}, status=status.HTTP_200_OK)
    
class DiscountCreateView(generics.CreateAPIView):
    queryset = Discounts.objects.all()
    serializer_class = DiscountSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

class DiscountListView(generics.ListAPIView):
    queryset = Discounts.objects.all()
    serializer_class = DiscountSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

class DiscountUpdateView(generics.UpdateAPIView):
    queryset = Discounts.objects.all()
    serializer_class = DiscountSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

class DiscountProductSpecificView(generics.RetrieveAPIView):
    serializer_class = DiscountSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return Discounts.objects.all()
    
    def get(self, request, *args, **kwargs):
        try:
            item = Discounts.objects.filter(product=kwargs['pk']).values()
        except(Discounts.DoesNotExist):
            return Response({"message": "No discounts found on the particular product"})
        return Response(item.values(), status=status.HTTP_200_OK)

class DiscountRetrieveView(generics.RetrieveAPIView):
    queryset = Discounts.objects.all()
    serializer_class = DiscountSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

class DiscountDeleteView(generics.DestroyAPIView):
    queryset = Discounts.objects.all()
    serializer_class = DiscountSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

    def destroy(self, request, *args, **kwargs):
        dis = Discounts.objects.get(pk=kwargs['pk'])
        dis.delete()
        return Response({"message":"Discount deleted successfully!"}, status=status.HTTP_200_OK)
        
    








