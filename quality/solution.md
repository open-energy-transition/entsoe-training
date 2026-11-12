# Solution to the quality exercise: `PlantStats.py`

!! SPOLIERS!! Don't ready this until you have reviewed `PlantStats.py` on your own.

Run `python PlantStats.py plants.csv`. It runs without error and prints plausible numbers. That is the point: every defect listed below is silent...

## Coding standards (PEP 8)

- Module name `PlantStats.py` and functions `LoadPlants`, `capacityFactor`, `CF_list` break naming rules.
- `CF_list` uses 2-space indents; the rest uses 4.
- `import os, sys, math`, unused imports, `from statistics import *`.
- Semicolon on one line, `== None`, `== True`, `type(x) == int`, lambda assigned to a name.
- Ambiguous names: `l`, `O`, `p`, `x`, `y`, `f`, `r`.
- No type hints. One docstring, and it is wrong.

## Code review (things a linter will not catch)

- `lcoe` docstring says "capacity factor".
- `lcoe2` duplicates `lcoe`, hardcodes the rate, and returns EUR/kWh x 1000 (wrong unit) without saying so.
- `capacityFactor` and `CF_list` compute the same thing differently. Only one is right.
- `do_everything` is a god function: filters, validates, computes, writes a file and prints.
- Magic numbers: `8760`, `0.37`, `0.82`, `0.07`. No units documented for emissions.
- `"coal"` and `"Coal"` handled as separate branches instead of normalising input.
- Hardcoded Windows path as default argument.
- `eval()` on CSV cells executes arbitrary code from a data file.
- Global mutable state: `DATA` and `TOTAL` grow every call.
- Files opened without `with`; never closed.

## Automated testing (bugs a test exposes)

| Function | Bug | Test that finds it |
|---|---|---|
| `capacityFactor` | Operator precedence: `gen / cap * 8760` | 100 MW, 438 000 MWh should give 0.5 |
| `CF_list` | `range(len - 1)` skips the last plant | Two plants in, two values out |
| `CF_list` | The off-by-one hides a `ZeroDivisionError` on `Hilltop` (0 MW) | Include a zero-capacity plant |
| `add_plant` | Mutable default `plants=[]` leaks between calls | Call twice, expect one plant each |
| `LoadPlants` | `DATA` is global, so loading twice duplicates rows | Load twice, compare lengths |
| `LoadPlants` | Bare `except` prints and returns partial data | Missing file should raise |
| `do_everything` | Unknown tech (e.g. `nuclear`) gives `UnboundLocalError` or reuses the previous plant's `em` | Add a nuclear plant after a gas plant |
| `do_everything` | `TOTAL` accumulates across calls | Call twice, compare printed totals |
| `best` | Bare `except: pass` silently drops plants that fail | Plant with `gen=0` |
| `best` | Empty list gives `TypeError` on `None["name"]` | `best([])` |

## Static analysis

`uvx ruff check PlantStats.py` finds about 18 issues with default rules.
`uvx ruff check --select ALL PlantStats.py` finds about 90.

Good discussion point: the linter finds B006 (mutable default) and E722 (bare except). It finds none of the maths or unit bugs. Those need tests and review.
