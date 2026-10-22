from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("products", views.ProductViewSet)
router.register("boxes", views.BoxViewSet)
router.register("orders", views.OrderViewSet)

urlpatterns = [
    path("recommend/", views.recommend, name="recommend"),
    path("", include(router.urls)),
]
