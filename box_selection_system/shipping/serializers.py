from django.db import transaction
from rest_framework import serializers

from .models import Box, Order, OrderItem, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "sku", "name", "length_mm", "width_mm", "height_mm", "weight_g"]


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = [
            "id", "name", "inner_length_mm", "inner_width_mm", "inner_height_mm",
            "max_weight_g", "cost", "is_active",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    sku = serializers.SlugRelatedField(
        source="product", slug_field="sku", queryset=Product.objects.all()
    )

    class Meta:
        model = OrderItem
        fields = ["sku", "quantity"]


def validate_unique_skus(items):
    if not items:
        raise serializers.ValidationError("At least one item is required.")
    skus = [i["product"].sku for i in items]
    if len(skus) != len(set(skus)):
        raise serializers.ValidationError("Each SKU may appear only once; use quantity instead.")
    return items


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    recommended_box = BoxSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "reference", "created_at", "items", "recommended_box"]
        read_only_fields = ["created_at"]

    def validate_items(self, items):
        return validate_unique_skus(items)

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        OrderItem.objects.bulk_create(OrderItem(order=order, **i) for i in items)
        return order


class RecommendRequestSerializer(serializers.Serializer):
    """Ad-hoc request: 'which box would these items need?' without saving an order."""

    items = OrderItemSerializer(many=True)

    def validate_items(self, items):
        return validate_unique_skus(items)


def recommendation_to_dict(rec):
    chosen = rec.chosen_check
    return {
        "recommended_box": BoxSerializer(rec.box).data if rec.box else None,
        "message": "OK" if rec.box else "No single active box can hold this order.",
        "summary": {
            "item_count": rec.item_count,
            "total_weight_g": rec.total_weight_g,
            "total_volume_mm3": rec.total_volume_mm3,
            "fill_percent": chosen.fill_percent if chosen else None,
            "weight_percent": chosen.weight_percent if chosen else None,
        },
        "boxes_considered": [
            {"box": c.box.name, "cost": str(c.box.cost), "fits": c.fits, "reason": c.reason}
            for c in rec.checks
        ],
    }
