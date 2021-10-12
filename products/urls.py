# -*- coding: utf-8 -*-
from django.conf.urls import include
from django.urls import path
from rest_framework.routers import SimpleRouter

from products.views import ProductModelViewSet

router = SimpleRouter()
router.register("", ProductModelViewSet, "products")


urlpatterns = [
    path("", include(router.urls)),
]
