from random import randint, uniform

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from mixer.backend.django import mixer
from orders.models import Order, OrderDetail
from products.models import Product
from rest_framework.test import APIClient


class BaseModelViewSetTestCase(TestCase):
    url_name = ""

    def setUp(self):
        self.client = APIClient()

    def _post_create(self, data):
        return self.client.post(reverse(f"{self.url_name}-list"), data, format="json")

    def _get_list(self):
        return self.client.get(reverse(f"{self.url_name}-list"), format="json")

    def _obtain_detail_payload(self, data=None, id_value=None):
        return {"path": reverse(f"{self.url_name}-detail", kwargs={"pk": id_value}), "data": data, "format": "json"}

    def _get_retrive(self, id_value=None):
        return self.client.get(**self._obtain_detail_payload(id_value=id_value))

    def _patch_partial_update(self, data, id_value=None):
        return self.client.patch(**self._obtain_detail_payload(data, id_value))

    def _put_update(self, data, id_value=None):
        return self.client.put(reverse(f"{self.url_name}-detail", kwargs={"pk": id_value}), data=data)

    def _delete_destroy(self, id_value=None):
        return self.client.delete(reverse(f"{self.url_name}-detail", kwargs={"pk": id_value}))


def update_kwargs(kwargs, field_name, method_to_create=None, default_value=None):
    value = kwargs.get(field_name)
    if value is None:
        if method_to_create:
            kwargs[field_name] = method_to_create()
        else:
            kwargs[field_name] = default_value


class ProductFactory:
    @staticmethod
    def create_product(**kwargs):
        update_kwargs(kwargs, "price", default_value=round(uniform(1000, 2000), 2))
        update_kwargs(kwargs, "stock", default_value=randint(10, 200))
        product = mixer.blend(Product, **kwargs)
        return product


class OrderFactory:
    @staticmethod
    def create_order(**kwargs):
        order_details = kwargs.pop("order_details", None)
        update_kwargs(kwargs, "date", default_value=now())
        order = mixer.blend(Order, **kwargs)
        if order_details:
            for order_detail in order_details:
                order_detail.update({"order": order})
                OrderFactory.create_order_detail(**order_detail)
        return order

    @staticmethod
    def create_order_detail(**kwargs):
        update_kwargs(kwargs, "order", method_to_create=OrderFactory.create_order)
        product_id = kwargs.pop("product_id", None)
        if product_id is None:
            kwargs["product"] = ProductFactory.create_product()
        else:
            kwargs["product"] = Product.objects.get(id=product_id)
        order_detail = mixer.blend(OrderDetail, **kwargs)
        return order_detail


dolar_si_mocked_data = [
    {
        "casa": {
            "agencia": "349",
            "compra": "98,53",
            "decimales": "2",
            "nombre": "Dolar Oficial",
            "variacion": "0",
            "venta": "104,53",
            "ventaCero": "TRUE",
        }
    },
    {
        "casa": {
            "agencia": "310",
            "compra": "182,00",
            "decimales": "2",
            "nombre": "Dolar Blue",
            "variacion": "0",
            "venta": "185,00",
            "ventaCero": "TRUE",
        }
    },
    {
        "casa": {
            "agencia": "311",
            "compra": "No Cotiza",
            "decimales": "3",
            "nombre": "Dolar Soja",
            "variacion": "0",
            "venta": "0",
            "ventaCero": "TRUE",
        }
    },
]
