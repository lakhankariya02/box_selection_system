"""
Box recommendation: glue between the database models and the pure packer.

Selection rule:
  A box is a candidate only if ALL of these hold
    - total order weight <= box max weight
    - total item volume <= box volume (cheap early rejection)
    - every single item fits in the box in some rotation
    - the packer finds a real arrangement for all items together
  Among candidates pick the lowest cost; ties go to the smaller box
  (less void fill), then to the box name so the result is deterministic.
"""

from dataclasses import dataclass, field

from .models import Box
from .packing import Item, fits_individually, pack


class RecommendationError(ValueError):
    pass


@dataclass
class BoxCheck:
    box: Box
    fits: bool
    reason: str = ""
    fill_percent: float = 0.0
    weight_percent: float = 0.0


@dataclass
class Recommendation:
    box: Box | None
    total_weight_g: int
    total_volume_mm3: int
    item_count: int
    checks: list = field(default_factory=list)

    @property
    def chosen_check(self):
        return next((c for c in self.checks if self.box and c.box.pk == self.box.pk), None)


def build_items(lines):
    """
    Turn (product, quantity) pairs into a flat list of packer Items.
    Quantity 3 of a product becomes 3 separate items, because each
    physical unit needs its own space in the box.
    """
    items = []
    for product, quantity in lines:
        if quantity < 1:
            raise RecommendationError(f"Quantity for {product.sku} must be at least 1.")
        for n in range(quantity):
            items.append(
                Item(
                    name=f"{product.sku}#{n + 1}",
                    length=product.length_mm,
                    width=product.width_mm,
                    height=product.height_mm,
                    weight=product.weight_g,
                )
            )
    if not items:
        raise RecommendationError("Order has no items.")
    return items


def check_box(box, items, total_weight, total_volume):
    if total_weight > box.max_weight_g:
        return BoxCheck(box, False, f"Too heavy: {total_weight} g > max {box.max_weight_g} g.")
    if total_volume > box.volume_mm3:
        return BoxCheck(box, False, "Items' total volume is larger than the box volume.")
    for item in items:
        if not fits_individually(item, box.dimensions):
            return BoxCheck(box, False, f"{item.name} does not fit in any orientation.")
    result = pack(items, box.dimensions)
    if not result.fits:
        names = ", ".join(i.name for i in result.unplaced)
        return BoxCheck(box, False, f"Could not find an arrangement for: {names}.")
    return BoxCheck(
        box,
        True,
        "Fits.",
        fill_percent=round(100 * total_volume / box.volume_mm3, 1),
        weight_percent=round(100 * total_weight / box.max_weight_g, 1),
    )


def recommend_box(lines, boxes=None):
    """
    lines: iterable of (Product, quantity)
    boxes: optional queryset/list of boxes; defaults to all active boxes.
    """
    items = build_items(lines)
    if boxes is None:
        boxes = Box.objects.filter(is_active=True)
    boxes = list(boxes)

    total_weight = sum(i.weight for i in items)
    total_volume = sum(i.volume for i in items)
    checks = [check_box(b, items, total_weight, total_volume) for b in boxes]

    candidates = [c for c in checks if c.fits]
    best = min(candidates, key=lambda c: (c.box.cost, c.box.volume_mm3, c.box.name), default=None)

    return Recommendation(
        box=best.box if best else None,
        total_weight_g=total_weight,
        total_volume_mm3=total_volume,
        item_count=len(items),
        checks=checks,
    )


def recommend_for_order(order, save=True):
    lines = [(oi.product, oi.quantity) for oi in order.items.select_related("product")]
    rec = recommend_box(lines)
    if save:
        order.recommended_box = rec.box
        order.save(update_fields=["recommended_box"])
    return rec
