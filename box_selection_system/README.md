# Box Selection System (Django)

A small Django + Django REST Framework service that recommends the **cheapest shipping box
that can physically hold an order**, taking dimensions, rotation and weight into account.

## Problem

Each product has dimensions and a weight. Each box has internal dimensions, a maximum
weight and a cost. For an order (products × quantities), pick the box the warehouse
should use.

## How the recommendation works

For every active box, the order is checked in this order (cheapest checks first):

| # | Check | Why |
|---|-------|-----|
| 1 | Total weight ≤ box max weight | Hard safety limit |
| 2 | Total item volume ≤ box volume | Fast rejection, no packing needed |
| 3 | Every item fits on its own in some rotation | e.g. a 550 mm umbrella never fits a 400 mm box |
| 4 | A real 3D arrangement exists (packer) | Volume alone is misleading: two 100 mm cubes don't fit a 150×150×100 box even though the volume does |

Among boxes that pass all four, the system picks the **lowest cost**. Ties go to the
**smaller box** (less empty space and void fill), then to the box name so the result is always the same.

The response also lists **every box that was considered and why it was rejected**,
so a warehouse user can see the reasoning.

### The packer (`shipping/packing.py`)

Exact 3D bin packing is NP-hard, so I use a **guillotine best-fit heuristic**:

1. Sort the items (largest volume first).
2. Keep a list of free rectangular spaces, which starts as the whole box.
3. Place each item in the **smallest** free space it fits in, trying all 6 rotations.
4. Split the leftover space into 3 non-overlapping spaces (right / front / top).
5. If some item can't be placed, retry with other orderings (longest edge first,
   largest footprint first).

**Trade-off:** the heuristic is *conservative*. When it says "fits", the placements are
guaranteed to be inside the box and non-overlapping (a property test checks this on random
inputs). It may occasionally miss a valid arrangement and suggest a slightly bigger box.
For a warehouse that is the safe kind of mistake: an unneeded bigger box costs a few cents,
while a box that's too small means re-packing.

### Assumptions / out of scope

- Units are integers: **millimetres** and **grams**. This avoids float rounding problems.
- Items are rigid cuboids and are placed axis-aligned (no tilting at angles).
- No padding/clearance is added. Product dimensions are assumed to include their own packaging.
- Items may be stacked on any side (no "this side up" or fragility rules).
- One box per order. If nothing fits, the API returns `recommended_box: null` with
  per-box reasons. Splitting an order across several boxes would be the next feature.

## Project layout

```
config/                 Django project settings and root URLs
shipping/
  models.py             Product, Box, Order, OrderItem
  packing.py            Pure-Python 3D packer (no Django imports)
  services.py           Box selection rules (uses the models and the packer)
  serializers.py        DRF serializers and response formatting
  views.py / urls.py    REST API
  admin.py              Admin, including a "Recommend box" action on orders
  management/commands/seed_data.py   Sample boxes and products
  tests/                test_packing.py, test_services.py, test_api.py
.github/workflows/tests.yml          CI: runs the test suite on every push
```

## Setup (Windows / PowerShell)

Requires Python 3.12 (also works on 3.11+).

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data            # loads 5 boxes and 6 products
python manage.py createsuperuser      # optional, for /admin
python manage.py runserver
```

On macOS/Linux, use `python3 -m venv venv` and `source venv/bin/activate`.

## API

Base URL: `http://127.0.0.1:8000/api/`. DRF's browsable API works in the browser too.

| Method | URL | Purpose |
|--------|-----|---------|
| GET/POST | `/api/products/` | List / create products |
| GET/POST | `/api/boxes/` | List / create boxes |
| GET/POST | `/api/orders/` | List / create orders (with nested items) |
| POST | `/api/orders/{id}/recommend-box/` | Recommend a box and **save** it on the order |
| POST | `/api/recommend/` | Recommend a box for items **without** saving an order |

### Example

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/recommend/ `
  -H "Content-Type: application/json" `
  -d '{\"items\":[{\"sku\":\"MUG-01\",\"quantity\":2},{\"sku\":\"BOOK-01\",\"quantity\":3}]}'
```

Response (shortened):

```json
{
  "recommended_box": {"name": "Medium", "cost": "0.90", "...": "..."},
  "message": "OK",
  "summary": {"item_count": 5, "total_weight_g": 1900, "total_volume_mm3": 4500000,
              "fill_percent": 40.0, "weight_percent": 38.0},
  "boxes_considered": [
    {"box": "Small",  "cost": "0.50", "fits": false, "reason": "Items' total volume is larger than the box volume."},
    {"box": "Medium", "cost": "0.90", "fits": true,  "reason": "Fits."},
    "..."
  ]
}
```

Creating an order:

```json
POST /api/orders/
{"reference": "ORD-100", "items": [{"sku": "BOOK-01", "quantity": 2}]}
```

Validation: unknown SKU, empty item list, quantity < 1, duplicate SKU lines and zero
dimensions are all rejected with HTTP 400.

## Tests

```powershell
python manage.py test -v 2
```

30 tests across three levels:

- **Packer unit tests**: exact fits, rotation needed, too long in every orientation,
  "volume OK but shape not", plus a randomized property test (50 random orders) that
  checks placements never overlap and never go outside the box.
- **Service tests**: cheapest box, weight limit overrides size, long item → long box,
  inactive boxes ignored, tie-break, nothing fits, empty/zero-quantity orders.
- **API tests**: endpoints, validation errors, order create → recommend → saved.

The output of the latest run is in [TEST_OUTPUT.md](TEST_OUTPUT.md). GitHub Actions runs
the same suite on every push (see the Actions tab of the repository).

## Possible improvements

- Split shipments across several boxes when no single box fits.
- Per-product rules: fragile, "this side up", can't be stacked, padding in mm.
- Optimise for total cost (box price + carrier price based on dimensional weight).
- Cache recommendations for repeated identical baskets.
