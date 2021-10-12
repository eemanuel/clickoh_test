from rest_framework.viewsets import ModelViewSet

from orders.models import Order, OrderDetail
from orders.serializers import OrderDetailSerializer, OrderSerializer


class OrderModelViewSet(ModelViewSet):
    queryset = Order.objects.all().prefetch_related("order_details")
    serializer_class = OrderSerializer
    http_method_names = (
        "get",
        "post",
        "patch",
        "delete",
    )  # put isn't allowed because id cant be completely updated


class OrderDetailModelViewSet(ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    http_method_names = (
        "post",
        "put",
        "patch",
        "delete",
    )  # only to create, update or delete
