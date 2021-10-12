# -*- coding: utf-8 -*-
from django.conf.urls import include
from django.urls import path
from rest_framework.routers import SimpleRouter

from orders.views import OrderDetailModelViewSet, OrderModelViewSet

router = SimpleRouter()
router.register("orders", OrderModelViewSet, "orders")
router.register("order-details", OrderDetailModelViewSet, "order-details")


urlpatterns = [
    path("", include(router.urls)),
]
