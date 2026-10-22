from io import StringIO

from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from shipping.models import Box, Order, Product


class ApiTests(APITestCase):
    def setUp(self):
        call_command("seed_data", stdout=StringIO())

    def test_recommend_endpoint(self):
        resp = self.client.post(
            reverse("recommend"), {"items": [{"sku": "MUG-01", "quantity": 1}]}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["recommended_box"]["name"], "Small")
        self.assertEqual(len(resp.data["boxes_considered"]), Box.objects.count())

    def test_recommend_unknown_sku(self):
        resp = self.client.post(
            reverse("recommend"), {"items": [{"sku": "NOPE", "quantity": 1}]}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recommend_duplicate_sku_rejected(self):
        items = [{"sku": "MUG-01", "quantity": 1}, {"sku": "MUG-01", "quantity": 2}]
        resp = self.client.post(reverse("recommend"), {"items": items}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recommend_empty_items_rejected(self):
        resp = self.client.post(reverse("recommend"), {"items": []}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recommend_zero_quantity_rejected(self):
        resp = self.client.post(
            reverse("recommend"), {"items": [{"sku": "MUG-01", "quantity": 0}]}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recommend_nothing_fits(self):
        resp = self.client.post(
            reverse("recommend"), {"items": [{"sku": "LAMP-01", "quantity": 20}]}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(resp.data["recommended_box"])

    def test_create_order_then_recommend(self):
        resp = self.client.post(
            reverse("order-list"),
            {"reference": "ORD-100", "items": [{"sku": "BOOK-01", "quantity": 2}, {"sku": "MUG-01", "quantity": 1}]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.data["id"]

        resp = self.client.post(reverse("order-recommend-box", args=[order_id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data["recommended_box"])

        order = Order.objects.get(pk=order_id)
        self.assertEqual(order.recommended_box.name, resp.data["recommended_box"]["name"])

    def test_product_crud(self):
        resp = self.client.post(
            reverse("product-list"),
            {"sku": "NEW-1", "name": "New", "length_mm": 10, "width_mm": 10, "height_mm": 10, "weight_g": 5},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(sku="NEW-1").exists())

    def test_product_zero_dimension_rejected(self):
        resp = self.client.post(
            reverse("product-list"),
            {"sku": "BAD", "name": "Bad", "length_mm": 0, "width_mm": 10, "height_mm": 10, "weight_g": 5},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
