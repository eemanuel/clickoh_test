from datetime import datetime

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import (CASCADE, CharField, DateTimeField, F, ForeignKey,
                              IntegerField, Sum)
from utils.models import TimeStampModel

from orders.requester import DolarSiRequester


class Order(TimeStampModel):
    id = CharField(max_length=20, primary_key=True)
    date = DateTimeField(default=datetime.now)

    class Meta:
        db_table = "orders"

    def __str__(self):
        return f"id={self.id}, date={self.date.strftime('%Y-%m-%d %H:%M:%S')}"

    def get_total(self):
        """Calculates the order's total price."""
        order_details = self.order_details.aggregate(total=Sum(F("product__price") * F("quantity")))
        return order_details["total"]

    def get_total_usd(self):
        """Get dolar_values, find dolar blue's buy value and return total in dolars"""
        dolar_values = DolarSiRequester().get_main_values()
        for dolar_value in dolar_values:
            stand = dolar_value["casa"]
            if stand["nombre"] == "Dolar Blue":
                break
        buy_value = float(stand["compra"].replace(",", "."))  # quizas Decimal
        return round(self.get_total() / buy_value, 2)


class OrderDetail(TimeStampModel):
    order = ForeignKey(Order, on_delete=CASCADE, related_name="order_details")
    product = ForeignKey("products.Product", on_delete=CASCADE, related_name="order_details")
    quantity = IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = "order_details"

    def __str__(self):
        return f"order={self.order.id}, product={self.product.id}, quantity={self.quantity}"
