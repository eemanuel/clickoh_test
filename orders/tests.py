from unittest.mock import patch

from rest_framework.exceptions import ErrorDetail
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_405_METHOD_NOT_ALLOWED)

from orders.models import Order, OrderDetail
from utils.tests import (BaseModelViewSetTestCase, OrderFactory,
                         ProductFactory, dolar_si_mocked_data)


class OrderBaseModelViewSetTestCase(BaseModelViewSetTestCase):
    def setUp(self):
        super().setUp()
        self.product = ProductFactory.create_product(stock=1000)
        self.product_2 = ProductFactory.create_product(stock=2500)
        create_data = {
            "id": "54321543215432154321",
            "date": "2020-03-20",
            "order_details": [{"product_id": self.product.id, "quantity": 77}],
        }
        self.order = OrderFactory.create_order(**create_data)
        assert self.order.order_details.count() == 1
        self.order_detail = self.order.order_details.last()
        self.order_detail.quantity = 100


class OrderModelViewSetTest(OrderBaseModelViewSetTestCase):
    url_name = "orders"

    def test_create_success(self):
        """Testing if a Order and OrderDetails are successfully created."""
        assert Order.objects.count() == 1
        assert OrderDetail.objects.count() == 1
        create_data = {
            "id": "12345678901234567890",
            "date": "2018-12-25",
            "order_details": [{"product_id": self.product.id, "quantity": 100}],
        }
        response = self._post_create(data=create_data)
        assert response.status_code == HTTP_201_CREATED
        assert Order.objects.count() == 2
        assert OrderDetail.objects.count() == 2
        data = response.data
        assert data["id"] == create_data["id"]
        assert create_data["date"] in data["date"]
        initial_order_details = create_data["order_details"]
        order_details = data["order_details"]
        assert len(initial_order_details) == len(order_details) == 1
        initial_order_detail = initial_order_details[0]
        order_detail = order_details[0]
        assert initial_order_detail["product_id"] == order_detail["product_id"]
        assert initial_order_detail["quantity"] == order_detail["quantity"]

    def test_create_bad_quantity(self):
        """Testing if a Order and OrderDetails are successfully created."""
        assert Order.objects.count() == 1
        assert OrderDetail.objects.count() == 1
        quantity = 7777
        create_data = {
            "id": "12345678901234567890",
            "date": "2018-12-25",
            "order_details": [{"product_id": self.product.id, "quantity": quantity}],
        }
        response = self._post_create(data=create_data)
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert Order.objects.count() == 1
        assert OrderDetail.objects.count() == 1
        data = response.data
        assert data[0]["non_field_errors"][0] == ErrorDetail(
            string=f"No se puede pedir {quantity} de {self.product.name}, pues solo quedan {self.product.stock}.",
            code="invalid",
        )

    @patch(
        "orders.requester.DolarSiRequester.get_main_values",
        return_value=dolar_si_mocked_data,
    )
    def test_list_success(self, *args):
        """Testing if all Order and OrderDetails are successfully listed and paginated."""
        products_count = 6
        for x in range(products_count):
            OrderFactory.create_order(
                order_details=[{"product_id": self.product.id, "quantity": 100}]
            )
        response = self._get_list()
        assert response.status_code == HTTP_200_OK
        data = response.data
        assert data["count"] == products_count + 1
        assert data["next"] is None
        assert data["previous"] is None
        results = data["results"]
        for result in results:
            for key in ["id", "created", "updated", "date", "total_pesos", "total_usd"]:
                assert result[key] is not None
            order_details = result["order_details"]
            for order_detail in order_details:
                for key in ["id", "created", "updated", "quantity", "order", "product"]:
                    assert order_detail[key] is not None

    @patch(
        "orders.requester.DolarSiRequester.get_main_values",
        return_value=dolar_si_mocked_data,
    )
    def test_retrive_success(self, *args):
        """Testing if a single Order and their OrderDetails are successfully detailed."""
        order = self.order
        response = self._get_retrive(id_value=order.id)
        assert response.status_code == HTTP_200_OK
        data = response.data
        for key in ["id", "created", "updated", "date", "total_pesos", "total_usd"]:
            assert data[key] is not None
        order_details = data["order_details"]
        for order_detail in order_details:
            for key in ["id", "created", "updated", "quantity", "order", "product"]:
                assert order_detail[key] is not None

    def test_partial_update_success(self):
        """Testing if a single Order and OrderDetails are partially updated successfully with PATCH method."""
        order = self.order
        old_date = order.date
        patch_data = {"date": "2018-12-25"}
        assert order.date == old_date
        response = self._patch_partial_update(data=patch_data, id_value=order.id)
        assert response.status_code == HTTP_200_OK
        order.refresh_from_db()
        assert patch_data["date"] in response.data["date"]
        assert (
            patch_data["date"]
            == order.date.strftime("%Y-%m-%d")
            != old_date.strftime("%Y-%m-%d")
        )

    def test_update_not_allowed(self):
        """Testing if PUT method is not allowed."""
        response = self._put_update(data={}, id_value=self.order_detail.id)
        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
        assert response.data["detail"] == ErrorDetail(
            string='Method "PUT" not allowed.', code="method_not_allowed"
        )

    def test_destroy_success(self):
        """Testing if a single Order and their OrderDetail are deleted."""
        assert Order.objects.count() == 1
        assert OrderDetail.objects.count() == 1
        response = self._delete_destroy(id_value=self.order.id)
        assert response.status_code == HTTP_204_NO_CONTENT
        assert Order.objects.count() == 0
        assert OrderDetail.objects.count() == 0


class OrderDetailModelViewSetTest(OrderBaseModelViewSetTestCase):
    url_name = "order-details"

    def test_create_success(self):
        """Testing if an OrderDetail is successfully created."""
        assert OrderDetail.objects.count() == 1
        create_data = {
            "product_id": self.product_2.id,
            "order_id": self.order.id,
            "quantity": 100,
        }
        response = self._post_create(data=create_data)
        assert response.status_code == HTTP_201_CREATED
        assert OrderDetail.objects.count() == 2
        data = response.data
        assert data["product"] == create_data["product_id"]
        assert data["order"] == create_data["order_id"]
        assert data["quantity"] == create_data["quantity"]

    def test_create_bad_product(self):
        """Testing if an OrderDetail is successfully created."""
        assert OrderDetail.objects.count() == 1
        product_id = self.product.id
        order_id = self.order.id
        create_data = {
            "product_id": product_id,
            "order_id": self.order.id,
            "quantity": 100,
        }
        response = self._post_create(data=create_data)
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert OrderDetail.objects.count() == 1
        assert response.data["order"][0] == ErrorDetail(
            string=f"Ya existe otro detalle con el producto {product_id} para la orden {order_id}.",
            code="invalid",
        )

    def test_list_not_allowed(self):
        """Testing if GET method (list) is not allowed."""
        response = self._get_list()
        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
        assert response.data["detail"] == ErrorDetail(
            string='Method "GET" not allowed.', code="method_not_allowed"
        )

    def test_retrive_not_allowed(self):
        """Testing if GET method (list) is not allowed."""
        response = self._get_retrive(id_value=self.order.id)
        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
        assert response.data["detail"] == ErrorDetail(
            string='Method "GET" not allowed.', code="method_not_allowed"
        )

    def test_partial_update_success(self):
        """Testing if a single OrderDetail is partially updated successfully with PATCH method."""
        order_detail = self.order_detail
        old_quantity = order_detail.quantity
        patch_data = {"quantity": 55}
        response = self._patch_partial_update(data=patch_data, id_value=order_detail.id)
        assert response.status_code == HTTP_200_OK
        order_detail.refresh_from_db()
        assert patch_data["quantity"] == order_detail.quantity != old_quantity

    def test_update_success(self):
        """Testing if a single OrderDetail is successfully updated with PUT method."""
        order_detail = self.order_detail
        order_2 = OrderFactory.create_order(
            order_details=[{"product_id": self.product.id, "quantity": 100}]
        )
        put_data = {
            "order_id": order_2.id,
            "product_id": self.product_2.id,
            "quantity": 55,
        }
        old_order_detail = dict(
            order_detail.__dict__
        )  # dict() is to avoid refresh with refresh_from_db()
        response = self._put_update(data=put_data, id_value=order_detail.id)
        assert response.status_code == HTTP_200_OK
        data = response.data
        order_detail.refresh_from_db()
        assert data["id"] == order_detail.id == old_order_detail["id"]
        assert (
            data["order"]
            == order_detail.order.id
            == put_data["order_id"]
            != old_order_detail["order_id"]
        )
        assert (
            data["product"]
            == order_detail.product.id
            == put_data["product_id"]
            != old_order_detail["product_id"]
        )
        assert (
            data["quantity"]
            == order_detail.quantity
            == put_data["quantity"]
            != old_order_detail["quantity"]
        )

    def test_destroy_success(self):
        """Testing if a single OrderDetail is deleted."""
        assert OrderDetail.objects.count() == 1
        response = self._delete_destroy(id_value=self.order_detail.id)
        assert response.status_code == HTTP_204_NO_CONTENT
        assert OrderDetail.objects.count() == 0
