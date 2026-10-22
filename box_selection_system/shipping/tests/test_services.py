from decimal import Decimal

from django.test import TestCase

from shipping.models import Box, Order, OrderItem, Product
from shipping.services import RecommendationError, recommend_box, recommend_for_order


def make_box(name, l, w, h, max_weight, cost, **kw):
    return Box.objects.create(
        name=name, inner_length_mm=l, inner_width_mm=w, inner_height_mm=h,
        max_weight_g=max_weight, cost=Decimal(cost), **kw,
    )


def make_product(sku, l, w, h, weight):
    return Product.objects.create(sku=sku, name=sku, length_mm=l, width_mm=w, height_mm=h, weight_g=weight)


class RecommendBoxTests(TestCase):
    def setUp(self):
        self.small = make_box("Small", 200, 150, 100, 2000, "0.50")
        self.medium = make_box("Medium", 300, 250, 150, 5000, "0.90")
        self.large = make_box("Large", 400, 300, 250, 10000, "1.50")
        self.long = make_box("Long", 600, 150, 150, 8000, "1.20")

        self.mug = make_product("MUG", 120, 90, 100, 350)
        self.book = make_product("BOOK", 200, 130, 30, 400)
        self.umbrella = make_product("UMB", 550, 80, 80, 600)
        self.brick = make_product("BRICK", 100, 100, 50, 2500)

    def test_picks_cheapest_box_that_fits(self):
        rec = recommend_box([(self.mug, 1)])
        self.assertEqual(rec.box, self.small)

    def test_quantity_pushes_to_bigger_box(self):
        # 4 mugs cannot fit in Small (only one row of 120 mm fits in 200 mm)
        rec = recommend_box([(self.mug, 4)])
        self.assertEqual(rec.item_count, 4)
        self.assertEqual(rec.box, self.medium)

    def test_weight_limit_rejects_box_that_is_big_enough(self):
        # one brick fits Small by size but is 2500 g > 2000 g limit
        rec = recommend_box([(self.brick, 1)])
        self.assertEqual(rec.box, self.medium)
        small_check = next(c for c in rec.checks if c.box == self.small)
        self.assertIn("Too heavy", small_check.reason)

    def test_long_item_chooses_long_box_not_largest(self):
        rec = recommend_box([(self.umbrella, 1)])
        self.assertEqual(rec.box, self.long)

    def test_no_box_fits(self):
        rec = recommend_box([(self.umbrella, 10)])
        self.assertIsNone(rec.box)
        self.assertTrue(all(not c.fits for c in rec.checks))
        self.assertTrue(all(c.reason for c in rec.checks))

    def test_inactive_box_is_ignored(self):
        self.small.is_active = False
        self.small.save()
        rec = recommend_box([(self.mug, 1)])
        self.assertEqual(rec.box, self.medium)

    def test_same_cost_prefers_smaller_box(self):
        cheap_big = make_box("CheapBig", 500, 500, 500, 9000, "0.50")
        rec = recommend_box([(self.mug, 1)])
        self.assertEqual(rec.box, self.small)
        self.assertNotEqual(rec.box, cheap_big)

    def test_mixed_order_totals(self):
        rec = recommend_box([(self.mug, 2), (self.book, 3)])
        self.assertEqual(rec.total_weight_g, 2 * 350 + 3 * 400)
        self.assertIsNotNone(rec.box)
        self.assertGreater(rec.chosen_check.fill_percent, 0)
        self.assertLessEqual(rec.chosen_check.fill_percent, 100)

    def test_empty_order_raises(self):
        with self.assertRaises(RecommendationError):
            recommend_box([])

    def test_zero_quantity_raises(self):
        with self.assertRaises(RecommendationError):
            recommend_box([(self.mug, 0)])

    def test_recommend_for_order_saves_box(self):
        order = Order.objects.create(reference="ORD-1")
        OrderItem.objects.create(order=order, product=self.mug, quantity=1)
        recommend_for_order(order)
        order.refresh_from_db()
        self.assertEqual(order.recommended_box, self.small)
