from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (FloatField, ModelSerializer,
                                        ValidationError)

from orders.models import Order, OrderDetail


class OrderDetailSerializer(ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = "__all__"

    def validate(self, attrs):
        product = attrs.get("product")
        quantity = attrs.get("quantity")
        if not product and not quantity:
            return super().validate(attrs)
        if not product:
            product = self.instance.product
        if not quantity:
            quantity = self.instance.quantity
        stock = product.stock
        if stock < quantity:
            raise ValidationError(f"No se puede pedir {quantity} de {product.name}, pues solo quedan {stock}.")
        return super().validate(attrs)

    def validate_order(self, order):
        product_ids = order.order_details.all().values_list("product_id", flat=True)
        if isinstance(self.initial_data, list):  # to many = True
            initial_product_ids = []
            for dictionary in self.initial_data:
                initial_product_ids.append(dictionary.get("product_id"))
            initial_product_ids = set(initial_product_ids)
            if len(initial_product_ids) != len(self.initial_data):  # if products are repeated.
                raise ValidationError(f"No puede duplicar productos en la misma orden.")
            for initial_product_id in initial_product_ids:
                if initial_product_id in product_ids:
                    raise ValidationError(
                        f"Ya existe otro detalle con el producto {initial_product_id} para la orden {order.id}."
                    )
        else:
            product_id = self.initial_data.get("product_id")
            if product_id in product_ids:
                raise ValidationError(f"Ya existe otro detalle con el producto {product_id} para la orden {order.id}.")
        return order

    def to_internal_value(self, data):
        new_data = {}
        product_id = data.get("product_id")
        order_id = data.get("order_id")
        quantity = data.get("quantity")
        if product_id:
            new_data.update({"product": product_id})
        if order_id:
            new_data.update({"order": order_id})
        if quantity:
            new_data.update({"quantity": quantity})
        return super().to_internal_value(new_data)


class OrderSerializer(ModelSerializer):
    order_details = SerializerMethodField()
    total_pesos = FloatField(source="get_total", required=False)
    total_usd = FloatField(source="get_total_usd", required=False)  # para porbar esto mockear

    class Meta:
        model = Order
        fields = "__all__"

    def get_order_details(self, order):
        try:
            order_details = self.initial_data.get("order_details")
        except AttributeError:  # because self shouldn't have initial_data.
            order_details = None
        if not order_details:  # because is a GET.
            return OrderDetailSerializer(order.order_details.all(), many=True).data
        order_detail_data = []
        for order_detail in order_details:
            id_dict = {
                "order_id": order.id,
                "product_id": order_detail.get("product_id"),
                "quantity": order_detail.get("quantity"),
            }
            order_detail_data.append(id_dict)
        serializer = OrderDetailSerializer(data=order_detail_data, many=True)
        if not serializer.is_valid():
            order.delete()
            raise ValidationError(serializer.errors)
        serializer.save()
        return serializer.initial_data
