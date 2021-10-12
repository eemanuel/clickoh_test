from rest_framework.serializers import ModelSerializer

from products.models import Product


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {"id": {"required": False}}
