from rest_framework.exceptions import ErrorDetail
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)

from products.models import Product
from utils.tests import BaseModelViewSetTestCase, ProductFactory


class ProductModelViewSetTestCase(BaseModelViewSetTestCase):
    url_name = "products"

    def setUp(self):
        super().setUp()
        create_data = {
            "id": "54321543215432154321",
            "name": "Name",
            "price": 777,
            "stock": 100,
        }
        self.product = ProductFactory.create_product(**create_data)

    def test_create_success(self):
        """Testing if a Product is successfully created."""

        assert Product.objects.count() == 1
        create_data = {
            "id": "12345678901234567890",
            "name": "Producto",
            "price": 777,
            "stock": 55,
        }
        response = self._post_create(data=create_data)
        assert response.status_code == HTTP_201_CREATED
        assert Product.objects.count() == 2
        data = response.data
        assert data["id"] == create_data["id"]
        assert data["name"] == create_data["name"]
        assert data["price"] == create_data["price"]
        assert data["stock"] == create_data["stock"]

    def test_create_bad_data(self):
        """Testing if a Product is not created with bad data."""
        request_data = {
            "id": "123456789012345678901",
            "name": False,
            "price": -66,
            "stock": -33,
        }
        assert Product.objects.count() == 1
        response = self._post_create(data=request_data)
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert Product.objects.count() == 1
        data = response.data
        assert data["id"][0] == ErrorDetail(
            string="Ensure this field has no more than 20 characters.",
            code="max_length",
        )
        assert data["name"][0] == ErrorDetail(
            string="Not a valid string.", code="invalid"
        )
        assert (
            data["price"][0]
            == data["stock"][0]
            == ErrorDetail(
                string="Ensure this value is greater than or equal to 0.",
                code="min_value",
            )
        )

    def test_list_success(self):
        """Testing if all Products are successfully listed and paginated."""
        products_count = 6
        for x in range(products_count):
            ProductFactory.create_product()
        response = self._get_list()
        assert response.status_code == HTTP_200_OK
        data = response.data
        assert data["count"] == products_count + 1
        assert data["next"] is None
        assert data["previous"] is None
        results = data["results"]
        for result in results:
            for key in ["id", "created", "updated", "name", "price", "stock"]:
                assert result[key] is not None

    def test_retrive_success(self):
        """Testing if a single Product is successfully detailed."""
        product = self.product
        response = self._get_retrive(id_value=product.id)
        assert response.status_code == HTTP_200_OK
        data = response.data
        assert data["id"] == product.id
        assert data["name"] == product.name
        assert data["price"] == product.price
        assert data["stock"] == product.stock

    def test_partial_update_success(self):
        """Testing if a single Product is partially updated successfully with PATCH method."""
        product = self.product
        old_stock = product.stock
        patch_data = {"stock": 0}
        assert product.stock == old_stock
        response = self._patch_partial_update(data=patch_data, id_value=product.id)
        assert response.status_code == HTTP_200_OK
        product.refresh_from_db()
        assert (
            response.data["stock"] == patch_data["stock"] == product.stock != old_stock
        )

    def test_update_success(self):
        """Testing if a single Product is successfully updated with PUT method."""
        product = self.product
        put_data = {
            "name": "Another Name",
            "price": 1000,
            "stock": 7,
        }
        old_product = dict(
            product.__dict__
        )  # dict() is to avoid refresh with refresh_from_db()
        response = self._put_update(data=put_data, id_value=product.id)
        assert response.status_code == HTTP_200_OK
        data = response.data
        product.refresh_from_db()
        assert data["id"] == product.id == old_product["id"]
        assert data["name"] == product.name == put_data["name"] != old_product["name"]
        assert (
            data["price"] == product.price == put_data["price"] != old_product["price"]
        )
        assert (
            data["stock"] == product.stock == put_data["stock"] != old_product["stock"]
        )

    def test_destroy_success(self):
        """Testing if a single Product is deleted."""
        assert Product.objects.count() == 1
        response = self._delete_destroy(id_value=self.product.id)
        assert response.status_code == HTTP_204_NO_CONTENT
        assert Product.objects.count() == 0
