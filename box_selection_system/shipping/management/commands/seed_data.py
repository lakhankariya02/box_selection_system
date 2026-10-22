from decimal import Decimal

from django.core.management.base import BaseCommand

from shipping.models import Box, Product

BOXES = [
    # name, L, W, H (mm), max weight (g), cost
    ("Small", 200, 150, 100, 2000, Decimal("0.50")),
    ("Medium", 300, 250, 150, 5000, Decimal("0.90")),
    ("Large", 400, 300, 250, 10000, Decimal("1.50")),
    ("Long", 600, 150, 150, 8000, Decimal("1.20")),
    ("XL", 600, 400, 400, 20000, Decimal("2.50")),
]

PRODUCTS = [
    # sku, name, L, W, H (mm), weight (g)
    ("MUG-01", "Coffee mug", 120, 90, 100, 350),
    ("BOOK-01", "Paperback book", 200, 130, 30, 400),
    ("PHONE-01", "Phone in retail box", 170, 90, 60, 450),
    ("LAMP-01", "Desk lamp", 350, 200, 200, 1800),
    ("UMB-01", "Umbrella", 550, 80, 80, 600),
    ("KETTLE-01", "Electric kettle", 250, 200, 250, 1500),
]


class Command(BaseCommand):
    help = "Load sample boxes and products (safe to run more than once)."

    def handle(self, *args, **options):
        for name, l, w, h, max_w, cost in BOXES:
            Box.objects.update_or_create(
                name=name,
                defaults=dict(
                    inner_length_mm=l, inner_width_mm=w, inner_height_mm=h,
                    max_weight_g=max_w, cost=cost, is_active=True,
                ),
            )
        for sku, name, l, w, h, weight in PRODUCTS:
            Product.objects.update_or_create(
                sku=sku,
                defaults=dict(name=name, length_mm=l, width_mm=w, height_mm=h, weight_g=weight),
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(BOXES)} boxes and {len(PRODUCTS)} products."))
