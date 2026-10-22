from django.contrib import admin, messages

from .models import Box, Order, OrderItem, Product
from .services import RecommendationError, recommend_for_order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "length_mm", "width_mm", "height_mm", "weight_g"]
    search_fields = ["sku", "name"]


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = [
        "name", "inner_length_mm", "inner_width_mm", "inner_height_mm",
        "max_weight_g", "cost", "is_active",
    ]
    list_filter = ["is_active"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["reference", "created_at", "recommended_box"]
    inlines = [OrderItemInline]
    actions = ["recommend_boxes"]

    @admin.action(description="Recommend box for selected orders")
    def recommend_boxes(self, request, queryset):
        for order in queryset:
            try:
                rec = recommend_for_order(order)
            except RecommendationError as exc:
                self.message_user(request, f"{order}: {exc}", messages.ERROR)
                continue
            if rec.box:
                self.message_user(request, f"{order}: {rec.box}")
            else:
                self.message_user(request, f"{order}: no box fits", messages.WARNING)
