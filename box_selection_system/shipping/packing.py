"""
Pure-Python 3D packing logic (no Django imports, so it is easy to unit test).

Units: all lengths are integer millimetres, all weights are integer grams.
Integers avoid floating point surprises like 0.1 + 0.2 != 0.3.

Algorithm: guillotine "best-fit" heuristic.
  1. Sort items largest volume first (big items are hardest to place).
     If that fails, retry with other orderings (see ORDERINGS).
  2. Keep a list of free rectangular spaces, starting with the whole box.
  3. For each item, try every free space and each of the 6 axis-aligned
     rotations. Pick the smallest free space the item fits in.
  4. Place the item in the corner of that space and split what is left into
     three non-overlapping spaces (right, front, top).

The heuristic is conservative: if it says the items fit, they really do
(every placement is inside the box and placements never overlap). It may
occasionally say "does not fit" for an arrangement a human could find,
which is the safe direction for a warehouse.
"""

from dataclasses import dataclass, field
from itertools import permutations


@dataclass(frozen=True)
class Item:
    name: str
    length: int
    width: int
    height: int
    weight: int

    @property
    def volume(self):
        return self.length * self.width * self.height

    def orientations(self):
        # set() removes duplicates, e.g. a cube has only one orientation
        return sorted(set(permutations((self.length, self.width, self.height))))


@dataclass(frozen=True)
class Space:
    x: int
    y: int
    z: int
    length: int
    width: int
    height: int

    @property
    def volume(self):
        return self.length * self.width * self.height

    def can_hold(self, dims):
        l, w, h = dims
        return l <= self.length and w <= self.width and h <= self.height


@dataclass(frozen=True)
class Placement:
    item: Item
    x: int
    y: int
    z: int
    length: int
    width: int
    height: int


@dataclass
class PackResult:
    fits: bool
    placements: list = field(default_factory=list)
    unplaced: list = field(default_factory=list)


def fits_individually(item, box_dims):
    """True if the item fits in an empty box in at least one rotation."""
    box_sorted = sorted(box_dims)
    item_sorted = sorted((item.length, item.width, item.height))
    return all(i <= b for i, b in zip(item_sorted, box_sorted))


def _split(space, dims):
    """Split the leftover of `space` after placing `dims` at its corner."""
    l, w, h = dims
    pieces = [
        # right of the item, full width and height of the space
        Space(space.x + l, space.y, space.z, space.length - l, space.width, space.height),
        # in front of the item, only as long as the item
        Space(space.x, space.y + w, space.z, l, space.width - w, space.height),
        # on top of the item, only the item's footprint
        Space(space.x, space.y, space.z + h, l, w, space.height - h),
    ]
    return [p for p in pieces if p.volume > 0]


# Different orders in which to place items. Volume-first alone fails on cases
# like a long flat item that must lie on the floor before a bulky item goes on
# top, so we also try longest-edge-first and largest-footprint-first.
ORDERINGS = [
    lambda i: (-i.volume, i.name),
    lambda i: (-max(i.length, i.width, i.height), -i.volume, i.name),
    lambda i: (-sorted((i.length, i.width, i.height))[1] * max(i.length, i.width, i.height), i.name),
]


def pack(items, box_dims):
    """Try to pack `items` into a box with inner dimensions `box_dims`.

    Each ordering is tried in turn; the first one that places everything wins.
    If none succeed, the attempt that placed the most items is returned.
    """
    best = None
    for key in ORDERINGS:
        result = _pack_in_order(sorted(items, key=key), box_dims)
        if result.fits:
            return result
        if best is None or len(result.unplaced) < len(best.unplaced):
            best = result
    return best


def _pack_in_order(items, box_dims):
    length, width, height = box_dims
    free = [Space(0, 0, 0, length, width, height)]
    placements = []
    unplaced = []

    for item in items:
        best = None
        for space in free:
            for dims in item.orientations():
                if not space.can_hold(dims):
                    continue
                # smallest space first, then lowest position (stack from the floor)
                score = (space.volume, space.z, space.y, space.x)
                if best is None or score < best[0]:
                    best = (score, space, dims)

        if best is None:
            unplaced.append(item)
            continue

        _, space, dims = best
        free.remove(space)
        free.extend(_split(space, dims))
        placements.append(Placement(item, space.x, space.y, space.z, *dims))

    return PackResult(fits=not unplaced, placements=placements, unplaced=unplaced)
