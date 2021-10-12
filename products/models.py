from django.core.validators import MinValueValidator
from django.db.models import (CASCADE, CharField, FloatField,
                              PositiveIntegerField)
from utils.models import TimeStampModel


class Product(TimeStampModel):
    id = CharField(max_length=20, primary_key=True)
    name = CharField(max_length=50)
    price = FloatField(validators=[MinValueValidator(0)])  # clavar Decimal
    stock = PositiveIntegerField()

    class Meta:
        db_table = "products"

    def __str__(self):
        return f"id={self.id}, name={self.name}, price={self.price}, stock={self.stock}"
