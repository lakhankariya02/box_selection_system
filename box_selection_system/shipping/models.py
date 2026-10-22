from django.core.validators import MinValueValidator
from django.db import models

# All dimensions are stored in millimetres and weights in grams (integers).
positive = [MinValueValidator(1)]


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    length_mm = models.PositiveIntegerField(validators=positive)
    width_mm = models.PositiveIntegerField(validators=positive)
    height_mm = models.PositiveIntegerField(validators=positive)
    weight_g = models.PositiveIntegerField(validators=positive)

    class Meta:
        ordering = ["sku"]

    def __str__(self):
        return f"{self.sku} - {self.name}"


class Box(models.Model):
    name = models.CharField(max_length=100, unique=True)
    inner_length_mm = models.PositiveIntegerField(validators=positive)
    inner_width_mm = models.PositiveIntegerField(validators=positive)
    inner_height_mm = models.PositiveIntegerField(validators=positive)
    max_weight_g = models.PositiveIntegerField(validators=positive)
    cost = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True, help_text="Inactive boxes are never recommended.")

    class Meta:
        ordering = ["cost", "name"]
        verbose_name_plural = "boxes"

    def __str__(self):
        return self.name

    @property
    def dimensions(self):
        return (self.inner_length_mm, self.inner_width_mm, self.inner_height_mm)

    @property
    def volume_mm3(self):
        return self.inner_length_mm * self.inner_width_mm * self.inner_height_mm


class Order(models.Model):
    reference = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    recommended_box = models.ForeignKey(
        Box, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.reference


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=positive)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["order", "product"], name="unique_product_per_order")
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.sku}"
