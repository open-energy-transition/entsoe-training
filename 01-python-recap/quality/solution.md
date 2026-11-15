# Solution to the quality exercise: `PlantStats.py`

!! SPOILERS !! Don't read this until you have reviewed `PlantStats.py` on your own.

Run `python PlantStats.py plants.csv`. It runs without error and prints plausible numbers. That is the point: every defect listed below is silent...

## Part 1: Issues by quality dimension

Each issue has an ID. Part 2 refers to these IDs.

### Readability: can others understand what has been done?

| ID | Issue |
|---|---|
| RD1 | Module `PlantStats.py` and functions `LoadPlants`, `capacityFactor`, `CF_list` break PEP 8 naming rules. |
| RD2 | Ambiguous names: `l`, `O`, `p`, `x`, `y`, `f`, `r`. |
| RD3 | `CF_list` uses 2-space indents; the rest uses 4. |
| RD4 | `import os, sys, math` on one line, unused imports, `from statistics import *`. |
| RD5 | Non-idiomatic code: semicolon, `== None`, `== True`, `type(x) == int`, lambda assigned to a name. |
| RD6 | No type hints. Module comment says nothing. One docstring, and it is wrong: `lcoe` says "capacity factor". |
| RD7 | Magic numbers `8760`, `0.37`, `0.82`, `0.07`. No units for emissions. `lcoe2` returns EUR/kWh x 1000 without saying so. |
| RD8 | `do_everything` nests five `if` levels deep. |

### Maintainability: is the code modular and decoupled?

| ID | Issue |
|---|---|
| MA1 | Duplication: `lcoe2` copies `lcoe` with a hardcoded rate. Capacity factor exists three times: `capacityFactor`, `CF_list` and inline in `do_everything`. |
| MA2 | `do_everything` is a god function: filters, validates, computes, writes a file and prints. |
| MA3 | Global mutable state: `DATA`, `TOTAL` and the rate `r`. |
| MA4 | Hardcoded Windows path as a default argument. |
| MA5 | `"coal"` and `"Coal"` are separate branches. An `if/elif` chain holds data that belongs in a lookup table. |
| MA6 | Computation has side effects: it writes `results.json` to the working directory and prints. |

### Reliability & correctness: does the code do what it should?

| ID | Issue |
|---|---|
| RC1 | `capacityFactor`: operator precedence, `gen / cap * 8760` instead of `gen / (cap * 8760)`. |
| RC2 | `CF_list`: `range(len - 1)` skips the last plant. This hides a `ZeroDivisionError` on `Hilltop` (0 MW). |
| RC3 | `add_plant`: mutable default `plants=[]` leaks plants between calls. |
| RC4 | `LoadPlants`: global `DATA` duplicates rows when you load twice. |
| RC5 | `LoadPlants`: bare `except` prints a message and returns partial data. A missing file does not fail. |
| RC6 | `do_everything`: unknown tech (e.g. `nuclear`) gives `UnboundLocalError`, or reuses the previous plant's `em`. |
| RC7 | `do_everything`: `TOTAL` accumulates across calls. |
| RC8 | `do_everything`: plants with zero capacity, zero life or non-numeric capacity are dropped without a warning. |
| RC9 | `best`: `except: pass` silently drops plants that fail. `best([])` gives `TypeError` on `None["name"]`. |
| RC10 | `lcoe2` returns a value in the wrong unit. |

### Security: is the software kept up to date? Are security flaws patched?

| ID | Issue |
|---|---|
| SE1 | `eval()` on CSV cells executes arbitrary code from a data file. |
| SE2 | The default path exposes a user name and local folder layout. |
| SE3 | Bare `except` also catches `KeyboardInterrupt` and `SystemExit`, and hides every failure. |
| SE4 | `do_everything` overwrites `results.json` in the current directory without asking. |
| SE5 | The script declares no Python version and no dependencies. Nothing tells you when it needs an update. |

### Efficiency & performance: does the code use a reasonable amount of resources?

| ID | Issue |
|---|---|
| EF1 | `best` recomputes `lcoe(O)` on every iteration: 2n LCOE calls instead of n. |
| EF2 | `lcoe` loops over every year of life and computes the discount factor twice per year. A closed-form annuity factor needs one calculation. |
| EF3 | `DATA` grows on every call to `LoadPlants`: memory grows without limit. |
| EF4 | Files are opened without `with` and never closed: leaked file handles. |
| EF5 | The main block computes capacity factors twice: in `do_everything` and in `CF_list`. |

## Part 2: Fixes by practice

### Coding standards (PEP 8)

| Fix | Resolves |
|---|---|
| Rename to `plant_stats.py`, `load_plants`, `capacity_factor`, `capacity_factors`. | RD1 |
| Use descriptive names: `factors`, `cheapest`, `plant`, `path`, `discount_rate`. | RD2 |
| Use 4-space indents everywhere. Let `ruff format` enforce it. | RD3 |
| One import per line. Delete `os`, `math` and the wildcard import. | RD4 |
| Use `is None`, `if out:`, `isinstance(x, (int, float))`. Replace the lambda with `statistics.mean`. Remove the semicolon. | RD5 |
| Add type hints. Use a `TypedDict` or `dataclass` for a plant. Write docstrings that state inputs, outputs and units. | RD6 |

### Code review (things a linter will not catch)

| Fix | Resolves |
|---|---|
| Name constants with units: `HOURS_PER_YEAR = 8760`, `DISCOUNT_RATE = 0.07`, `EMISSION_FACTORS_T_PER_MWH = {"gas": 0.37, "coal": 0.82, "wind": 0.0, "solar": 0.0}`. | RD7, MA5 |
| Delete `lcoe2`. If callers need EUR/MWh, convert at the call site with a named unit. | MA1, RC10 |
| Keep one `capacity_factor(plant)`. Build every list with it. | MA1, RC1, EF5 |
| Split `do_everything` into `filter_by_tech`, `plant_metrics`, `write_results(path)` and a `main` that prints. | MA2, MA6, RD8 |
| Remove globals. Functions take inputs and return new values. Compute the total with `sum(...)`. | MA3, RC4, RC7, EF3 |
| Make the CSV path a required CLI argument (e.g. `argparse`). Make the output path explicit. | MA4, SE2, SE4 |
| Normalise tech with `.lower()` on load. Look up emissions in the table and raise `KeyError` on unknown tech. | MA5, RC6 |
| Replace `eval` with `float()` and `int()`. Better: read with `csv.DictReader` and validate each row. | SE1 |
| Remove bare `except`. Let errors propagate (fail fast). Raise `ValueError` on invalid plants instead of skipping them. | RC5, RC8, RC9, SE3 |
| Open files with `with`. | EF4 |
| Write `best` as `min(plants, key=lcoe)["name"]`. It computes each LCOE once and raises on an empty list. | EF1, RC9 |
| Compute LCOE with an annuity factor, or precompute the discount factors once. | EF2 |
| Declare `requires-python` and dependencies in `pyproject.toml` or the pixi manifest. Keep the lock file current. | SE5 |

### Automated testing (bugs a test exposes)

| Function | Bug | Test that finds it | Resolves |
|---|---|---|---|
| `capacityFactor` | Operator precedence: `gen / cap * 8760` | 100 MW, 438 000 MWh should give 0.5 | RC1 |
| `CF_list` | `range(len - 1)` skips the last plant | Two plants in, two values out | RC2 |
| `CF_list` | The off-by-one hides a `ZeroDivisionError` on `Hilltop` (0 MW) | Include a zero-capacity plant | RC2 |
| `add_plant` | Mutable default `plants=[]` leaks between calls | Call twice, expect one plant each | RC3 |
| `LoadPlants` | `DATA` is global, so loading twice duplicates rows | Load twice, compare lengths | RC4 |
| `LoadPlants` | Bare `except` prints and returns partial data | Missing file should raise | RC5 |
| `LoadPlants` | `eval` executes cell content | A cell `__import__('os').getcwd()` should raise `ValueError` | SE1 |
| `do_everything` | Unknown tech (e.g. `nuclear`) gives `UnboundLocalError` or reuses the previous plant's `em` | Add a nuclear plant after a gas plant | RC6 |
| `do_everything` | `TOTAL` accumulates across calls | Call twice, compare printed totals | RC7 |
| `best` | Bare `except: pass` silently drops plants that fail | Plant with `gen=0` | RC9 |
| `best` | Empty list gives `TypeError` on `None["name"]` | `best([])` | RC9 |

Use `pytest.mark.parametrize` for the numeric cases. Use `tmp_path` for file tests, so no test writes to the repository.

### Static analysis

`uvx ruff check PlantStats.py` finds about 18 issues with default rules.
`uvx ruff check --select ALL PlantStats.py` finds about 90.

| Tool or rule set | Finds | Resolves |
|---|---|---|
| `ruff` defaults (`E`, `F`) | Unused and wildcard imports (F401, F403), `== None` (E711), `type() ==` (E721), bare `except` (E722), lambda assignment (E731), ambiguous names (E741) | RD2, RD4, RD5, SE3 |
| `ruff` `N` (pep8-naming) | Function and variable names (N802, N806). It does not flag the module name here. | RD1 |
| `ruff` `ANN`, `D` | Missing type hints and docstrings | RD6 |
| `ruff` `B` (bugbear) | Mutable default argument (B006) | RC3 |
| `ruff` `S` (bandit) | `eval` (S307), `except: pass` (S110) | SE1, RC9 |
| `ruff` `SIM102`, `C901` | Nested `if`, high complexity | RD8, MA2 |
| `ruff` `SIM115` | `open` without `with` | EF4 |
| `ruff` `PLW0603` | `global` statements | MA3 |
| `mypy` or `pyright` (type checkers, after adding hints) | `None["name"]`, wrong argument types | RC9 |
| `pip-audit` or Dependabot (dependency vulnerability scanners) | Outdated or vulnerable dependencies | SE5 |

Run `ruff` and the type checker in pre-commit and CI.

Good discussion point: the linter finds B006 (mutable default) and E722 (bare except). It finds none of the maths or unit bugs (RC1, RC2, RC10), and none of the magic numbers (RD7). Those need tests and review.
