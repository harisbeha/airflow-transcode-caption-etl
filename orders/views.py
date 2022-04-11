from rest_framework.viewsets import ModelViewSet
from service.custom_auth import CustomAuthentication
from orders.serializers import OrderItemSerializer, OutputProductSerializer
from orders.models import Cart, OrderItem, OutputProduct
from orders.forms import *


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.none()
    serializer_class = OrderItemSerializer
    authentication_classes = [CustomAuthentication]

    def get_queryset(self):
        qs = OrderItem.objects.filter(user=request.user)
        return qs

class OutputProductViewSet(ModelViewSet):
    queryset = OutputProduct.objects.none()
    serializer_class = OutputProductSerializer
    authentication_classes = [CustomAuthentication]

    def get_queryset(self):
        qs = OutputProduct.objects.filter(user=request.user)
        return qs
