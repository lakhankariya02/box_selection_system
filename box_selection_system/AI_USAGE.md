# AI Usage

> **TODO (candidate):** This file was drafted from the actual session log. Before submitting,
> read through it, correct anything that is wrong, and replace every `TODO` with your own words.

## Tools used

- **Claude Code** (Anthropic, model Claude Opus 5.5) in the terminal on Windows. It created the
  virtual environment, scaffolded the Django project, wrote the code, tests and docs, and ran the tests.
- TODO: list anything else you used (ChatGPT, Copilot, docs, Stack Overflow...).

## Prompts

Initial prompt (verbatim):

> can you help me completer this assigenmtn start to finesh crea a virtual envarmtn setup django
> i already have python inslaeed if you need any help ask me like chnage the python version or
> any external help [assignment PDF attached]

TODO: add any follow-up prompts you gave.

## What the AI produced and what was accepted / rejected

| Output | Decision | Reason |
|--------|----------|--------|
| Python 3.12 venv (3.11, 3.12 and 3.14 were installed) | Accepted | Well supported by Django 5.2 and DRF |
| Integer mm / grams instead of floats | Accepted | Avoids rounding errors in comparisons |
| Guillotine best-fit 3D packer instead of an exact solver | Accepted | Exact bin packing is NP-hard; a conservative heuristic is enough for a few items per order |
| Volume-only check ("sum of volumes ≤ box volume") | **Rejected** as the only rule | Wrong: two 100 mm cubes have less volume than a 150×150×100 box but don't fit. Kept only as a fast pre-check, with a test proving the case |
| Volume-first ordering as the only packing order | **Rejected** after a failing test | See "Mistakes found" |
| Tie-break: same cost → smaller box | Accepted | Less void fill |
| TODO: anything you changed or disagreed with | | |

## Mistakes found

1. **Packer missed a perfect fit.** Test `test_mixed_sizes` puts three items (300×200×100,
   100×200×100, 400×200×50) into a 400×200×150 box. Their total volume is exactly the box volume and
   they do fit, with the flat 400 mm item on the floor. The first version sorted items only by volume,
   so it placed the bulky item on the floor first. After that the 400 mm item had no room, and the test
   failed (`AssertionError: False is not true`).
   **Fix:** `pack()` now tries several item orderings (volume, longest edge, footprint) and accepts
   the first one that places everything. After the fix, all 30 tests passed.
2. TODO: anything you found while reviewing the code yourself.

## Verification steps

- `python manage.py check`: no issues.
- `python manage.py test -v 2`: 30 tests pass (see `TEST_OUTPUT.md`).
- A property test packs 50 random orders and asserts that no placement leaves the box or overlaps another.
  This is a check on the AI-written packer that doesn't rely on trusting it.
- Manual end-to-end run: `seed_data`, then `runserver`, then real HTTP calls:
  - 2 mugs + 3 books → **Medium** (Small rejected: volume too large). 40 % fill, 38 % weight.
  - 1 umbrella (550 mm) → **Long** (1.20), not XL (2.50). This is the expected cheapest box.
- TODO: describe what you checked by hand (e.g. did you work out one example on paper?).
