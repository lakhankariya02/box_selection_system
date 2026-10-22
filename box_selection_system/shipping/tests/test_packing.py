"""Unit tests for the pure packing algorithm (no database needed)."""

import random
from unittest import TestCase

from shipping.packing import Item, fits_individually, pack


def cube(name, size=100, weight=100):
    return Item(name, size, size, size, weight)


class FitsIndividuallyTests(TestCase):
    def test_exact_fit(self):
        self.assertTrue(fits_individually(Item("a", 200, 150, 100, 1), (200, 150, 100)))

    def test_fits_only_when_rotated(self):
        # 100 x 200 x 150 does not fit as-is in 200 x 150 x 100, but does when rotated
        self.assertTrue(fits_individually(Item("a", 100, 200, 150, 1), (200, 150, 100)))

    def test_too_long_in_every_orientation(self):
        self.assertFalse(fits_individually(Item("umbrella", 550, 80, 80, 1), (400, 300, 250)))


class PackTests(TestCase):
    def test_single_item(self):
        result = pack([cube("a")], (100, 100, 100))
        self.assertTrue(result.fits)
        self.assertEqual(len(result.placements), 1)

    def test_eight_cubes_fill_box_exactly(self):
        items = [cube(f"c{i}") for i in range(8)]
        self.assertTrue(pack(items, (200, 200, 200)).fits)

    def test_ninth_cube_does_not_fit(self):
        items = [cube(f"c{i}") for i in range(9)]
        result = pack(items, (200, 200, 200))
        self.assertFalse(result.fits)
        self.assertEqual(len(result.unplaced), 1)

    def test_volume_is_enough_but_shape_is_not(self):
        # 2 cubes = 2,000,000 mm3 < box 2,250,000 mm3, but they cannot sit side by side
        result = pack([cube("a"), cube("b")], (150, 150, 100))
        self.assertFalse(result.fits)

    def test_needs_rotation_to_pack_two_items(self):
        # each book is 200x130x30; box is 130x200x60 -> both fit only rotated and stacked
        books = [Item(f"b{i}", 200, 130, 30, 400) for i in range(2)]
        self.assertTrue(pack(books, (130, 200, 60)).fits)

    def test_mixed_sizes(self):
        # Exact fit (12,000,000 mm3 each): the 400x200x50 slab must go on the floor
        # first. Volume-first ordering alone fails this; a second ordering finds it.
        items = [Item("big", 300, 200, 100, 1), Item("s1", 100, 200, 100, 1), Item("s2", 400, 200, 50, 1)]
        self.assertTrue(pack(items, (400, 200, 150)).fits)

    def test_placements_are_inside_box_and_never_overlap(self):
        """Property check: whatever the packer places must be physically valid."""
        rng = random.Random(42)
        box = (300, 250, 200)
        for _ in range(50):
            items = [
                Item(f"i{n}", rng.randint(20, 150), rng.randint(20, 150), rng.randint(20, 150), 1)
                for n in range(rng.randint(1, 12))
            ]
            placements = pack(items, box).placements
            for p in placements:
                self.assertTrue(p.x >= 0 and p.y >= 0 and p.z >= 0)
                self.assertLessEqual(p.x + p.length, box[0])
                self.assertLessEqual(p.y + p.width, box[1])
                self.assertLessEqual(p.z + p.height, box[2])
                # rotated dims are a permutation of the original dims
                self.assertEqual(
                    sorted((p.length, p.width, p.height)),
                    sorted((p.item.length, p.item.width, p.item.height)),
                )
            for i, a in enumerate(placements):
                for b in placements[i + 1:]:
                    overlap = (
                        a.x < b.x + b.length and b.x < a.x + a.length
                        and a.y < b.y + b.width and b.y < a.y + a.width
                        and a.z < b.z + b.height and b.z < a.z + a.height
                    )
                    self.assertFalse(overlap, f"{a} overlaps {b}")
