"""Build hands-on-pypsa-components.ipynb, next to this script, from the cells below.

Edit this script, never the notebook. Run:
    python scripts/build_notebook.py [RESOLUTION]
RESOLUTION (hours per snapshot) defaults to 6. Use 12 for quick development runs.
"""

import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(__file__).resolve().parents[1] / "hands-on-pypsa-components.ipynb"
RESOLUTION = int(sys.argv[1]) if len(sys.argv) > 1 else 6

DSESM = "https://fneum.github.io/data-science-for-esm/dsesm"
CEM = f"{DSESM}/workshop-pypsa-cem/"
SC = f"{DSESM}/workshop-pypsa-sector-coupling/"
LP = f"{DSESM}/workshop-linopy/"
UG = "https://docs.pypsa.org/latest/user-guide"
REPO = "https://github.com/open-energy-transition/entsoe-training"
TYNDP = "https://2026.entsos-tyndp-scenarios.eu/download/"
OTYNDP = "https://github.com/open-energy-transition/open-tyndp/tree/tyndp-2026"

cells: list = []


def md(key: str, text: str) -> None:
    cells.append(new_markdown_cell(text.strip("\n"), id=key))


def code(key: str, text: str) -> None:
    cells.append(new_code_cell(text.strip("\n"), id=key))


# ================================================================ header
md(
    "title",
    """
<img src="images/OET_logo.png" alt="Open Energy Transition logo" width="220">

# Hands on with PyPSA components

ENTSO-E training · Tuesday 17 November 2026
""",
)

md(
    "objectives",
    """
:::{note} At the end of this notebook, you will be able to:

1. Build a simple sector-coupled model with capacity expansion.
2. Use PyPSA components (`Network`, `Bus`, `Load`, `Generator`, `StorageUnit`, `Store`, `Link`, `Process`, `Line`) to construct a model.
3. Use component parameters to define intended behaviours via constraints.
4. Explore the underlying optimisation problem created in linopy.
:::
""",
)

md(
    "intro",
    f"""
This notebook follows the course [Data Science for Energy System Modelling]({DSESM}/intro/) (F. Neumann, TU Berlin): the workshops [PyPSA: Capacity Expansion]({CEM}), [PyPSA: Sector-Coupling]({SC}) and [Linopy]({LP}). We reuse their steps, equations and code, together with the [PyPSA example notebooks](https://docs.pypsa.org/latest/examples/), and apply them to Germany, Austria and Switzerland with [TYNDP 2026]({TYNDP}) data. The section [Sources and licences](#sources-and-licences) lists every source.

| Step | Topic | Task |
|---|---|---|
| 1 | Capacity expansion for Germany | Only wind or only solar |
| 2 | Sector coupling with hydrogen | Expensive hydrogen storage |
| 3 | Parameters as constraints, and the grid | A CO₂ limit and its price |
| 4 | Under the hood: linopy | A higher renewable share |

:::{{note}}
For details on any component, see the [PyPSA documentation](https://docs.pypsa.org).
:::

:::{{warning}}
This is a stylised model for learning. Its numbers are not TYNDP results: one weather scenario of the TYNDP for 2035, greenfield, three countries, one node per country.
:::
""",
)

# ================================================================ setup
md(
    "env",
    f"""
## Setup

Install the environment as described in the [README]({REPO}#readme) of the training repository. The notebook also runs on [Google Colab](https://colab.research.google.com/). The solver is HiGHS (open source, no licence needed).
""",
)

md("imports-md", "Import the packages:")

code(
    "imports",
    """
import logging

import matplotlib.pyplot as plt
import pandas as pd
import pypsa
from pypsa.costs import annuity
""",
)

md(
    "options-md",
    "We show only warnings, hide the solver log and widen the figures. We also opt in to two PyPSA 2.0 defaults (string dtype and objective constant), which silences their warnings:",
)

code(
    "options",
    """
logging.basicConfig(level=logging.WARNING)
pypsa.options.params.optimize.log_to_console = False
plt.rcParams["figure.figsize"] = (15, 5)

pypsa.options.api.legacy_string_dtype = False
pypsa.options.params.optimize.include_objective_constant = False
""",
)

# ================================================================ data
md(
    "costs-md",
    f"""
## Technology data inputs

The costs for 2035 come from [PyPSA/technology-data](https://github.com/PyPSA/technology-data) v0.15.0, with a discount rate of 7 %. We pre-process them: convert units and set defaults. Then we apply the overwrites of [`data/custom_costs.csv`](https://github.com/open-energy-transition/open-tyndp/blob/tyndp-2026/data/custom_costs.csv) in [Open-TYNDP]({OTYNDP}), based on [TYNDP 2026]({TYNDP}) National Trends+ 2035:

- lifetime: 25 years for all technologies;
- OCGT: gas price 33.93 €/MWh, efficiency 42 %, variable cost 1.6 €/MWh, CO₂ factor 0.1744 t/MWh;
- electrolysis: efficiency 70 %;
- salt-cavern hydrogen storage: investment 1750 €/MWh, no fixed O&M;
- solar: utility-scale costs; wind and solar: near-zero variable costs.

All other values keep their technology-data values.
""",
)

code(
    "costs",
    """
year = 2035
url = f"https://raw.githubusercontent.com/PyPSA/technology-data/v0.15.0/outputs/costs_{year}.csv"
costs = pd.read_csv(url, index_col=[0, 1])

costs.loc[costs.unit.str.contains("/kW"), "value"] *= 1e3
costs.unit = costs.unit.str.replace("/kW", "/MW")

discount_rate = 0.07
defaults = {
    "FOM": 0,
    "VOM": 0,
    "efficiency": 1,
    "fuel": 0,
    "investment": 0,
    "CO2 intensity": 0,
    "discount rate": discount_rate,
}
costs = costs.value.unstack().fillna(defaults)

# Open-TYNDP overwrites, TYNDP 2026 National Trends+ 2035
costs.loc["solar"] = costs.loc["solar-utility"]
costs["lifetime"] = 25  # years
costs.loc["OCGT", ["fuel", "efficiency", "VOM", "CO2 intensity"]] = [33.93, 0.42, 1.6, 0.1744]
costs.at["electrolysis", "efficiency"] = 0.7
costs.loc["hydrogen storage underground", ["investment", "FOM"]] = [1750, 0]  # €/MWh, %/a
costs.loc[["onwind", "offwind", "solar"], "VOM"] = [0.015, 0.015, 0.01]  # €/MWh
""",
)

md(
    "annuity-md",
    """
The **annuity** annualises investment costs:

$$
a(r, n) = \\frac{r}{1-(1+r)^{-n}}
$$

where $r$ is the discount rate and $n$ is the lifetime. PyPSA provides it:
""",
)

code("annuity", "annuity(discount_rate, 25)")

md(
    "mc-md",
    "The short-term marginal generation costs (€/MWh), named `marginal_cost` in PyPSA:",
)

code("mc", 'costs["marginal_cost"] = costs["VOM"] + costs["fuel"] / costs["efficiency"]')

md(
    "cc-md",
    "The annualised investment costs (€/MW/a), named `capital_cost` in PyPSA. The fixed operation and maintenance cost (FOM) is a percentage of the investment per year:",
)

code(
    "cc",
    """
annuity_factor = annuity(costs["discount rate"], costs["lifetime"])
costs["capital_cost"] = (annuity_factor + costs["FOM"] / 100) * costs["investment"]
""",
)

md(
    "ts-md",
    f"""
## Loading time series data

The file `data/tyndp2026-nt2035-hourly-demand-wind-solar.csv` holds hourly time series of [TYNDP 2026]({TYNDP}) National Trends+ 2035, WS032 (as in [Open-TYNDP]({OTYNDP})), for Germany, Austria and Switzerland. The script `scripts/extract_tyndp.py` in this repository extracts it from the TYNDP download. First, the market-node electricity demand, in MW, the base unit of PyPSA:
""",
)

code(
    "demand",
    """
ts = pd.read_csv("data/tyndp2026-nt2035-hourly-demand-wind-solar.csv", index_col=0, parse_dates=True)
ts.columns = ts.columns.str.split(expand=True)  # (country, carrier)
demand = ts.xs("load", axis=1, level=1)
demand.resample("D").mean().div(1e3).plot(title="Electricity demand, daily mean", ylabel="GW")
""",
)

md(
    "cf-md",
    "Then the capacity factors of the Pan-European Climate Database (PECD) for onshore wind, offshore wind (Germany only) and utility-scale solar:",
)

code(
    "cf",
    """
cf = {country: ts[country].drop(columns="load") for country in demand.columns}
cf["DE"].head(3)
""",
)

md("cf-plot-md", "The weekly means show the seasons: more wind in winter, more sun in summer.")

code(
    "cf-plot",
    """
cf_weekly = pd.concat(cf, axis=1).resample("W").mean()
fig, axes = plt.subplots(1, 3, sharey=True)
fig.suptitle("Capacity factors, weekly mean")
for ax, tech in zip(axes, ["onwind", "offwind", "solar"]):
    cf_weekly.xs(tech, axis=1, level=1).plot(ax=ax, title=tech, ylabel="p.u.")
""",
)

md(
    "resolution-md",
    "We average the time series over blocks of 6 hours (by default), so that each optimisation runs in less than a minute. A higher resolution gives more accurate results, but takes longer. The resolution matters: a coarser one changes the system cost only a little, but it changes the capacity mix and the prices more. Read the numbers of this notebook as illustrations, not as results.",
)

code(
    "resolution",
    f"""
resolution = {RESOLUTION}
demand = demand.resample(f"{{resolution}}h").mean()
cf = {{country: df.resample(f"{{resolution}}h").mean() for country, df in cf.items()}}
""",
)

# ================================================================ step 1
md(
    "s1",
    f"""
# Step 1 · Capacity expansion for Germany

We start with one node for Germany: wind, solar, gas turbines and batteries. The capacities are **decision variables**, with costs in the objective. This is the **capacity expansion problem**:

\\begin{{equation*}}
    \\min_{{g,G}} \\quad \\underbrace{{\\sum_{{s,t}} w_t o_s g_{{s,t}}}}_{{\\text{{operation}}}} + \\underbrace{{\\sum_s c_s G_s + \\sum_r c_r G_r}}_{{\\text{{investment}}}}
\\end{{equation*}}
such that
\\begin{{align*}}
    d_t &= \\sum_s g_{{s,t}} + \\sum_r \\left(g_{{r,t,\\text{{dis}}}} - g_{{r,t,\\text{{ch}}}}\\right) & \\text{{energy balance}} \\\\
    0 &\\leq g_{{s,t}} \\leq \\hat{{g}}_{{s,t}} G_s & \\text{{generator limits}} \\\\
    0 &\\leq g_{{r,t,\\text{{dis/ch}}}} \\leq G_r & \\text{{storage dis/charge limits}} \\\\
    0 &\\leq e_{{r,t}} \\leq h_r G_r & \\text{{storage energy limits}} \\\\
    e_{{r,t}} &= e_{{r,t-1}} + w_t \\left(\\eta_r g_{{r,t,\\text{{ch}}}} - \\frac{{1}}{{\\eta_r}} g_{{r,t,\\text{{dis}}}}\\right) & \\text{{storage consistency}}
\\end{{align*}}

| Symbol | Meaning | Component | Attribute |
|---|---|---|---|
| $t$, $w_t$ | snapshot and its weighting in hours | `Network` | `snapshots`, `snapshot_weightings` |
| $d_t$ | demand | `Load` | `p_set` |
| $g_{{s,t}}$, $G_s$ | dispatch and capacity of generator $s$ | `Generator` | `p`, `p_nom` |
| $\\hat{{g}}_{{s,t}}$ | capacity factor | `Generator` | `p_max_pu` |
| $o_s$, $c_s$ | marginal cost and annualised capital cost | `Generator` | `marginal_cost`, `capital_cost` |
| $G_r$, $h_r$, $\\eta_r$, $c_r$ | power capacity, hours at full power, efficiency and annualised capital cost of storage unit $r$ | `StorageUnit` | `p_nom`, `max_hours`, `efficiency_store`/`_dispatch`, `capital_cost` |
| $e_{{r,t}}$ | state of charge | `StorageUnit` | `state_of_charge` |

See the [PyPSA optimisation overview]({UG}/optimization/overview/) for the full problem.
""",
)

md("network-md", "To build the model, we first create an empty network.")

code("network", "n = pypsa.Network()")

md(
    "box-md",
    """
:::{note} A network is a box
Think of the `Network` as an empty box. Each component you add puts a new feature in the box: a bus is a place where energy must balance, a load a demand, a generator a supply option. PyPSA turns the content of the box into an optimisation problem.
:::
""",
)

md(
    "bus-md",
    "Then, we add a single bus for Germany. `AC` is PyPSA's carrier name for the electricity grid. The nominal voltage `v_nom` (kV) matters only for the lines of Step 3.",
)

code("bus", 'n.add("Bus", "DE", carrier="AC", v_nom=380)')

md(
    "snapshots-md",
    "We tell the network that its snapshots $t$ are the time steps of the demand data. Each snapshot represents `resolution` hours, which is its weighting $w_t$:",
)

code(
    "snapshots",
    """
n.snapshots = demand.index
n.snapshot_weightings.loc[:, :] = resolution
n.snapshot_weightings.head(3)
""",
)

md(
    "carriers-md",
    "We add the technologies as carriers, with a colour for plots and their CO₂ emissions in t per MWh of fuel. PyPSA warns about components whose carrier is not defined:",
)

code(
    "carriers",
    """
carriers = ["onwind", "offwind", "solar", "OCGT", "battery storage", "AC"]
n.add(
    "Carrier",
    carriers,
    color=["dodgerblue", "navy", "gold", "indianred", "yellowgreen", "black"],
    co2_emissions=[costs.at[c, "CO2 intensity"] if c in costs.index else 0 for c in carriers],
)
""",
)

md("load-md", "Next, we add the demand time series $d_t$ to the model.")

code(
    "load",
    """
n.add("Load", "DE load", bus="DE", p_set=demand["DE"])
n.loads_t.p_set.div(1e3).plot(title="Electricity demand, Germany", ylabel="GW")
""",
)

md(
    "ocgt-md",
    "We add one dispatchable technology, an OCGT. `p_nom_extendable=True` turns its capacity $G_s$ into a decision variable.",
)

code(
    "ocgt",
    """
n.add(
    "Generator",
    "DE OCGT",
    bus="DE",
    carrier="OCGT",
    capital_cost=costs.at["OCGT", "capital_cost"],
    marginal_cost=costs.at["OCGT", "marginal_cost"],
    efficiency=costs.at["OCGT", "efficiency"],
    p_nom_extendable=True,
)
""",
)

md(
    "res-md",
    "The variable renewable generators also need their capacity factors $\\hat{g}_{s,t}$, via the attribute `p_max_pu`.",
)

code(
    "res",
    """
for tech in ["onwind", "offwind", "solar"]:
    n.add(
        "Generator",
        f"DE {tech}",
        bus="DE",
        carrier=tech,
        p_max_pu=cf["DE"][tech],
        capital_cost=costs.at[tech, "capital_cost"],
        marginal_cost=costs.at[tech, "marginal_cost"],
        p_nom_extendable=True,
    )
""",
)

md(
    "battery-md",
    "A battery is a `StorageUnit` with a fixed energy-to-power ratio $h_r$, the attribute `max_hours` (here 4 h). Its capital cost combines the inverter cost per MW and `max_hours` times the storage cost per MWh. `cyclic_state_of_charge=True` makes the state of charge at the end of the year equal to the one at the start.",
)

code(
    "battery",
    """
max_hours = 4  # h
n.add(
    "StorageUnit",
    "DE battery storage",
    bus="DE",
    carrier="battery storage",
    max_hours=max_hours,
    capital_cost=costs.at["battery inverter", "capital_cost"]
    + max_hours * costs.at["battery storage", "capital_cost"],
    efficiency_store=costs.at["battery inverter", "efficiency"],
    efficiency_dispatch=costs.at["battery inverter", "efficiency"],
    p_nom_extendable=True,
    cyclic_state_of_charge=True,
)
""",
)

md(
    "tables-md",
    "Each component type has a static table with one row per component, and time series in a second table:",
)

code("tables", "n.generators")

md(
    "opt1-md",
    'Then, we can solve the model. `io_api="direct"` hands the model to HiGHS in memory, instead of writing it to a file first: this is faster.',
)

code("opt1", 'n.optimize(io_api="direct")')

md("objective1-md", "The total system cost in billion euros per year:")

code("objective1", "n.objective / 1e9")

md("capacity1-md", "The optimised capacities in GW:")

code("capacity1", "n.statistics.optimal_capacity().div(1e3)  # GW")

md(
    "balance1-md",
    "The energy balance in TWh. Positive values are supply, negative values are consumption:",
)

code("balance1", "n.statistics.energy_balance().sort_values().div(1e6)  # TWh")

md(
    "nothing-md",
    "**No onshore wind.** Offshore wind costs 52 €/MWh at its mean capacity factor of 49 %, onshore wind 57 €/MWh at 26 %. The model builds only offshore wind. **Little battery.** The model builds 17 GW of battery, but OCGT remains the main source of flexibility. Without a CO₂ price, OCGT supplies 190 TWh, 31 % of the demand: Task 3 limits the emissions. The 6 h averages smooth out most of the day-night cycle that batteries exploit, so the model undervalues them. The dispatch of 1–14 February zooms on a windy start followed by a lull with little wind and sun. It shows how OCGT fills the gaps of wind and solar:",
)

code(
    "dispatch1",
    """
colors = n.generators.carrier.map(n.carriers.color).to_dict()
n.generators_t.p.loc["2035-02-01":"2035-02-14"].div(1e3).plot.area(color=colors, linewidth=0, title="Dispatch, Germany, 1–14 February", ylabel="GW")
""",
)

md(
    "save1-md",
    "We save the network to a file, to start the task and Step 2 from it.",
)

code("save1", 'n.export_to_netcdf("network-step1.nc");')

md(
    "task1",
    f"""
## Task 1 · Only wind or only solar

**5 min**

What if you could build only solar or only wind? Load the network of Step 1, remove a generator and re-optimise. Compare the capacities and the system cost with Step 1.

:::{{hint}}
`n_task = pypsa.Network("network-step1.nc")` loads the network. `n_task.remove("Generator", "DE solar")` removes a component: give its type and its name, or a list of names. Germany has two wind generators.
:::

*Source: [PyPSA: Capacity Expansion]({CEM}), Task 3.*
""",
)

code("task1-code", "# Your code here")

# ================================================================ step 2
md(
    "s2",
    f"""
# Step 2 · Sector coupling with hydrogen

We add a hydrogen demand, electrolysis, fuel cells and hydrogen storage. Each energy carrier gets its own `Bus` $i$ with its own energy balance. Converters $k$ connect the buses. Each converter has one dispatch variable $p_{{k,t}}$ with capacity $P_k$, and a rate $\\eta_{{i,k}}$ at each bus: negative for an input, positive for an output. Stores $q$ have a filling level $e_{{q,t}}$ and an energy capacity $E_q$. We keep the indices of Step 1: $s$ for generators and $r$ for storage units. Step 2 adds $i$ for buses, $k$ for converters and $q$ for stores:

\\begin{{equation*}}
    \\min \\quad \\underbrace{{\\ldots}}_{{\\text{{Step 1}}}} + \\underbrace{{\\sum_k c_k P_k + \\sum_q c_q E_q}}_{{\\text{{investment}}}}
\\end{{equation*}}
such that
\\begin{{align*}}
    d_{{i,t}} &= \\sum_s g_{{i,s,t}} + \\underbrace{{\\ldots}}_{{\\text{{storage units}}}} + \\sum_k \\eta_{{i,k}} p_{{k,t}} - \\sum_q \\frac{{e_{{q,t}} - e_{{q,t-1}}}}{{w_t}} & \\text{{energy balance at each bus}} \\\\
    0 &\\leq p_{{k,t}} \\leq P_k & \\text{{converter limits}} \\\\
    0 &\\leq e_{{q,t}} \\leq E_q & \\text{{store energy limits}}
\\end{{align*}}

| Symbol | Meaning | Component | Attribute |
|---|---|---|---|
| $i$ | bus, one per energy carrier | `Bus` | `carrier` |
| $t$, $w_t$ | snapshot and its weighting in hours, as in Step 1 | `Network` | `snapshots`, `snapshot_weightings` |
| $d_{{i,t}}$, $g_{{i,s,t}}$ | demand and generation at bus $i$ | `Load`, `Generator` | `p_set`, `p` |
| $p_{{k,t}}$, $P_k$ | dispatch and capacity of converter $k$ | `Link` / `Process` | `p0` / `p`, `p_nom` |
| $\\eta_{{i,k}}$ | rate of converter $k$ at bus $i$ | `Link` / `Process` | `efficiency` / `rate0`, `rate1` |
| $e_{{q,t}}$, $E_q$ | filling level and energy capacity of store $q$ | `Store` | `e`, `e_nom` |
| $c_k$, $c_q$ | annualised capital costs | `Link`, `Process`, `Store` | `capital_cost` |

PyPSA has two components for converters:

- **`Link`**: $p_{{k,t}}$ is the input at `bus0`, so $\\eta_{{\\text{{bus0}},k}} = -1$ and $\\eta_{{\\text{{bus1}},k}}$ = `efficiency`.
- **`Process`** (since PyPSA 1.2.0, April 2026): you set every rate yourself, `rate0`, `rate1`, … The bus with rate $\\pm 1$ sets the unit of $p_{{k,t}}$, $P_k$ and the costs.

[`Process`]({UG}/components/processes/) is an alternative to [`Link`]({UG}/components/links/), not a replacement: both give the same model. We build the electrolysis as a `Process` and the fuel cell as a `Link`, so you see both. The costs and efficiencies come from the assumptions loaded above. The hydrogen storage is an underground salt cavern.

*Source: [PyPSA: Sector-Coupling]({SC}), MIT/CC-BY-4.0.*
""",
)

md("h2bus-md", "We add a separate `Bus` for the hydrogen energy carrier:")

code("h2bus", 'n.add("Bus", "DE hydrogen", carrier="hydrogen")')

md(
    "electrolysis-md",
    "We add a `Process` for the electrolysis. It consumes electricity ($\\eta = -1$, the reference) and produces hydrogen ($\\eta = 0.7$):",
)

code(
    "electrolysis",
    """
n.add(
    "Process",
    "DE electrolysis",
    bus0="DE",
    bus1="DE hydrogen",
    carrier="electrolysis",
    rate0=-1,
    rate1=costs.at["electrolysis", "efficiency"],
    p_nom_extendable=True,
    capital_cost=costs.at["electrolysis", "capital_cost"],
)
""",
)

md(
    "fuelcell-md",
    "We add a `Link` for the fuel cell, which reconverts hydrogen to electricity:",
)

code(
    "fuelcell",
    """
n.add(
    "Link",
    "DE fuel cell",
    bus0="DE hydrogen",
    bus1="DE",
    carrier="fuel cell",
    efficiency=costs.at["fuel cell", "efficiency"],
    p_nom_extendable=True,
    capital_cost=costs.at["fuel cell", "capital_cost"],
)
""",
)

md(
    "h2store-md",
    "We add a `Store` for the hydrogen storage. Why not a `StorageUnit`, as for the battery? A `StorageUnit` has one power capacity for charging and discharging, and a fixed ratio `max_hours` between energy and power. This suits a battery, where one inverter does both. Hydrogen uses three assets with their own costs: the electrolysis charges, the fuel cell discharges and a tank or cavern holds the energy. A `Store` models only the energy, so the model sizes $E_q$, the electrolysis and the fuel cell independently. The electrolysis also serves the hydrogen demand directly, without passing through the storage. `e_cyclic=True` makes the filling level at the end equal the one at the start:",
)

code(
    "h2store",
    """
n.add(
    "Store",
    "DE hydrogen storage",
    bus="DE hydrogen",
    carrier="hydrogen storage",
    capital_cost=costs.at["hydrogen storage underground", "capital_cost"],
    e_nom_extendable=True,
    e_cyclic=True,
)
""",
)

md(
    "h2load-md",
    f"We add a constant hydrogen demand of 142.7 TWh per year, the German demand of [TYNDP 2026]({TYNDP}) National Trends+ 2035 (WS032). Our model has no imports, so it produces all of it in Germany:",
)

code(
    "h2load",
    """
p_set = 142.7e6 / 8760  # MW, 142.7 TWh/a
n.add("Load", "DE hydrogen demand", bus="DE hydrogen", carrier="hydrogen", p_set=p_set)  # MW
""",
)

md("h2carriers-md", "We add the new carriers, with colours for plots:")

code(
    "h2carriers",
    """
n.add(
    "Carrier",
    ["hydrogen", "electrolysis", "fuel cell", "hydrogen storage"],
    color=["cyan", "magenta", "orange", "purple"],
)
""",
)

md("opt2-md", "When we now optimise the model with the hydrogen demand...")

code("opt2", 'n.optimize(io_api="direct")')

md("objective2-md", "The total system cost in billion euros per year:")

code("objective2", "n.objective / 1e9")

md(
    "capacity2-md",
    "...we can see the sizing of the electrolysis and the hydrogen storage (GW and GWh). The fuel cell does not appear: the model builds none, because OCGT is the cheaper backup.",
)

code("capacity2", "n.statistics.optimal_capacity().div(1e3)  # GW, GWh")

md(
    "balance2-md",
    "The electricity balance in TWh. The electrolysis uses 204 TWh, against an electricity load of 622 TWh. OCGT output grows by 64 TWh from Step 1, about 31 % of the electrolysis use. OCGT sets the electricity price at 82.4 €/MWh most of the time. One more MWh of hydrogen then needs 1/0.7 MWh of electricity from OCGT, so the hydrogen price is mostly 82.4/0.7 ≈ 118 €/MWh. Gas power sets the price of hydrogen, although wind and solar produce most of it.",
)

code("balance2", 'n.statistics.energy_balance(bus_carrier="AC").sort_values().div(1e6)  # TWh')

md(
    "soc2-md",
    "The filling level of the hydrogen storage shows how it shifts energy in time. It holds at most 0.55 TWh, 1.4 days of hydrogen demand, and empties every month. Do not expect a seasonal storage from this model. OCGT, with unlimited gas and no CO₂ price, covers most shortages at 82.4 €/MWh, so storing hydrogen for months does not pay. The model also has one country, no imports and a constant hydrogen demand:",
)

code("soc2", 'n.stores_t.e.div(1e6).plot(title="Hydrogen storage filling level", ylabel="TWh")')

code("save2", 'n.export_to_netcdf("network-step2.nc");')

md(
    "task2",
    f"""
## Task 2 · Expensive hydrogen storage

**5 min**

Assume underground hydrogen storage is not available. Load `network-step2.nc`, increase the cost of hydrogen storage by a factor of 10 and re-optimise. How does the model react?

:::{{hint}}
The static table `n_task.stores` holds the cost. Change it with `n_task.stores.loc["DE hydrogen storage", "capital_cost"] *= 10`.
:::

*Source: [PyPSA: Sector-Coupling]({SC}), Task 1.*
""",
)

code("task2-code", "# Your code here")

# ================================================================ step 3
md(
    "s3",
    f"""
# Step 3 · Parameters as constraints, and the grid

We add Austria and Switzerland as buses $i$, connected by lines $\\ell$. Each line has a flow $f_{{\\ell,t}}$, a capacity $F_\\ell$ and a reactance $x_\\ell$. The energy balance of each bus now includes the flows, with the incidence matrix $K_{{i\\ell}}$:

\\begin{{equation*}}
    \\min \\quad \\underbrace{{\\ldots}}_{{\\text{{Steps 1, 2}}}} + \\underbrace{{\\sum_\\ell c_\\ell F_\\ell}}_{{\\text{{investment}}}}
\\end{{equation*}}
such that
\\begin{{align*}}
    d_{{i,t}} &= \\ldots - \\sum_\\ell K_{{i\\ell}} f_{{\\ell,t}} & \\text{{energy balance}} \\\\
    -F_\\ell &\\leq f_{{\\ell,t}} \\leq F_\\ell & \\text{{line limits}} \\\\
    0 &= \\sum_\\ell C_{{\\ell c}} x_\\ell f_{{\\ell,t}} & \\text{{KVL}} \\\\
    G_{{i,s}} &\\leq \\overline{{G}}_{{i,s}} & \\text{{generator capacity expansion limits}}
\\end{{align*}}

| Symbol | Meaning | Component | Attribute |
|---|---|---|---|
| $f_{{\\ell,t}}$, $F_\\ell$ | flow and capacity of line $\\ell$ | `Line` | `p0`, `s_nom` |
| $x_\\ell$ | reactance | `Line` | `x`, from `type` and `length` |
| $c_\\ell$ | annualised capital cost | `Line` | `capital_cost` |
| $K_{{i\\ell}}$ | $+1$ if line $\\ell$ starts at bus $i$, $-1$ if it ends there | `Line` | `bus0`, `bus1` |
| $C_{{\\ell c}}$ | $\\pm 1$ if line $\\ell$ is in loop $c$ | `Network` | computed by PyPSA |
| $G_{{i,s}}$, $\\overline{{G}}_{{i,s}}$ | capacity of generator $s$ at bus $i$ and its maximum | `Generator` | `p_nom`, `p_nom_max` |

In PyPSA, you rarely write a constraint yourself. You set a component parameter, and PyPSA writes the constraint:

| Intended behaviour | Parameter | Constraint |
|---|---|---|
| Weather-dependent output | `p_max_pu` (Step 1) | generator limits |
| Storage ends where it starts | `cyclic_state_of_charge`, `e_cyclic` (Steps 1, 2) | storage consistency |
| At most the planned wind and solar fleet | `p_nom_max` | generator capacity expansion limits |
| Meshed AC grid | `Line` with `type`, `length`, `s_nom_extendable` | line limits and KVL |
| Emission limit | `Carrier.co2_emissions` (Step 1) and a `GlobalConstraint` | CO₂ limit (Task 3) |

KVL is Kirchhoff's voltage law: in each closed loop $c$ of lines (matrix $C_{{\\ell c}}$), the flows split by reactance. Germany, Austria and Switzerland form one loop.

*Source: [PyPSA: Capacity Expansion]({CEM}); PyPSA user guide, [power flow]({UG}/optimization/power-flow/) and [capacity limits]({UG}/optimization/capacity-limits/), CC-BY-4.0.*
""",
)

md(
    "neighbours-md",
    "We add Austria and Switzerland with electricity only: a bus, a load and an OCGT each...",
)

code(
    "neighbours",
    """
for country in ["AT", "CH"]:
    n.add("Bus", country, carrier="AC", v_nom=380)
    n.add("Load", f"{country} load", bus=country, p_set=demand[country])
    n.add(
        "Generator",
        f"{country} OCGT",
        bus=country,
        carrier="OCGT",
        capital_cost=costs.at["OCGT", "capital_cost"],
        marginal_cost=costs.at["OCGT", "marginal_cost"],
        efficiency=costs.at["OCGT", "efficiency"],
        p_nom_extendable=True,
    )
""",
)

md("neighbours-res-md", "...and wind and solar with their own capacity factors.")

code(
    "neighbours-res",
    """
for country in ["AT", "CH"]:
    for tech in ["onwind", "solar"]:
        n.add(
            "Generator",
            f"{country} {tech}",
            bus=country,
            carrier=tech,
            p_max_pu=cf[country][tech],
            capital_cost=costs.at[tech, "capital_cost"],
            marginal_cost=costs.at[tech, "marginal_cost"],
            p_nom_extendable=True,
        )
""",
)

md(
    "pnommax-md",
    f"""
`p_nom_max` sets the maximum capacity $\\overline{{G}}_{{i,s}}$: the market-node wind and solar capacities of [TYNDP 2026]({TYNDP}) National Trends+ 2035, without rooftop solar, from the ENTSO-E Pan-European Market Modelling Database (PEMMDB). The model can build the planned fleet, but not more. The file `data/tyndp2026-nt2035-wind-solar-capacity.csv` holds the extract:
""",
)

code(
    "pnommax",
    """
p_nom_max = pd.read_csv("data/tyndp2026-nt2035-wind-solar-capacity.csv", index_col=0)["p_nom_max"]  # MW
n.generators.loc[p_nom_max.index, "p_nom_max"] = p_nom_max
p_nom_max
""",
)

md(
    "lines-md",
    f"""
We connect the three countries with three AC lines. The standard [line type]({UG}/components/line-types/) and the `length` give the reactance $x_\\ell$. The lengths are the distances between the country centres, rounded. The capital cost is the technology-data cost of an overhead line per MW and km. The model has no existing cross-border capacity: the grid is greenfield, so the model builds all of it.
""",
)

code(
    "lines",
    """
for bus0, bus1, length in [("DE", "AT", 500), ("DE", "CH", 510), ("AT", "CH", 480)]:
    n.add(
        "Line",
        f"{bus0}-{bus1}",
        bus0=bus0,
        bus1=bus1,
        type="Al/St 240/40 4-bundle 380.0",
        length=length,  # km
        s_nom_extendable=True,
        capital_cost=costs.at["HVAC overhead", "capital_cost"] * length,
    )
""",
)

code("opt3", 'n.optimize(io_api="direct")')

code("objective3", "n.objective / 1e9")

md(
    "capacity3-md",
    """
The generation capacities per country, in MW. `n.statistics` can plot each of its tables directly, with the carrier colours. Germany reaches its limits for offshore wind and solar, and builds onshore wind below its limit. Austria and Switzerland build all the solar they may, and Austria all its onshore wind; OCGT covers the rest. The model leaves out their large hydro fleets.
""",
)

code(
    "capacity3",
    """
fig, ax, grid = n.statistics.optimal_capacity.plot.bar(
    components="Generator", x="bus", y="value", color="carrier", stacked=True
)
ax.set(title="Generation capacity per country", ylabel="MW")
""",
)

md(
    "lines3-md",
    "The optimised line capacities in GW, 10 GW in total:",
)

code("lines3", "n.lines.s_nom_opt.div(1e3)  # GW")

md(
    "imports3-md",
    "The net imports per country in TWh, positive for imports. Switzerland imports, because its wind and solar limits are small. Germany and Austria export:",
)

code("imports3", 'n.statistics.energy_balance(components="Line", groupby="bus").div(1e6)  # TWh')

md(
    "emissions-md",
    "The `co2_emissions` of the carriers give the total emissions, in Mt per year:",
)

code(
    "emissions",
    """
co2_per_mwh = n.generators.carrier.map(n.carriers.co2_emissions) / n.generators.efficiency
emissions = n.generators_t.p * co2_per_mwh  # t/h
co2 = n.snapshot_weightings.generators @ emissions.sum(axis=1)  # t
round(float(co2) / 1e6, 1)  # Mt
""",
)

md(
    "emissions-text",
    "Without a CO₂ price, OCGT supplies 376 TWh, 39 % of the generation, at 0.42 t of CO₂ per MWh of electricity. The emissions grow with each step: 79 Mt in Step 1, 105 Mt with the hydrogen demand of Step 2, and 156 Mt with Austria, Switzerland and the limits on German offshore wind and solar.",
)

code("save3", 'n.export_to_netcdf("network-step3.nc");')

md(
    "task3",
    f"""
## Task 3 · A CO₂ limit and its price

**6 min**

Load `network-step3.nc`, cut the emissions by 30 % (limit them to `0.7 * co2`) and re-optimise. What is the CO₂ price? How do the capacities and the line capacities change?

The CO₂ price is the **dual value** (shadow price) of the limit: the change in system cost when its right-hand side grows by one unit, here one tonne. A larger right-hand side relaxes a `<=` constraint and lowers the cost, so its dual is negative. PyPSA stores it in `n_task.global_constraints.mu`, in €/t.

:::{{hint}}
A `GlobalConstraint` limits the sum of an attribute over the network. With `carrier_attribute="co2_emissions"`, PyPSA multiplies the `co2_emissions` of each carrier by its fuel use:

```python
n_task.add(
    "GlobalConstraint",
    "CO2Limit",
    carrier_attribute="co2_emissions",
    sense="<=",
    constant=...,  # t
)
```
:::

*Source: [PyPSA: Capacity Expansion]({CEM}), "Adding emission limits".*
""",
)

code("task3-code", "# Your code here")

# ================================================================ step 4
md(
    "s4",
    f"""
# Step 4 · Under the hood: linopy

`n.optimize()` does three things: it builds a [linopy](https://linopy.readthedocs.io) model, solves it and writes the results back into the network. We now build the model ourselves, read it and add a constraint.

*Source: [Linopy]({LP}); PyPSA user guide, [custom constraints]({UG}/optimization/custom-constraints/), CC-BY-4.0.*
""",
)

code(
    "model",
    """
n = pypsa.Network("network-step3.nc")
m = n.optimize.create_model()
m
""",
)

md(
    "names-md",
    """
`create_model()` returns the linopy model and also stores it as `n.model`, so `m` and `n.model` are the same object. Variables and constraints are named `Component-attribute`. `ext` marks extendable components. For example:

| Equation | Constraint name |
|---|---|
| energy balance | `Bus-nodal_balance` |
| generator limits | `Generator-ext-p-upper` |
| generator capacity expansion limits | `Generator-ext-p_nom-upper` |
| KVL | `Kirchhoff-Voltage-Law` |

Here is the energy balance of Germany in the first snapshot, with generators, the battery, the hydrogen converters and the lines:
""",
)

code("balance-con", 'm.constraints["Bus-nodal_balance"].sel(name="DE", snapshot=n.snapshots[0])')

md(
    "custom-md",
    """
Now we add a constraint that PyPSA does not offer: wind and solar must supply at least a share $\\alpha$ of all generation:

$$
\\sum_{t} w_t \\sum_{s \\in \\text{RES}} g_{s,t} \\geq \\alpha \\sum_{t} w_t \\sum_{s} g_{s,t}
$$

We write it with the linopy variable `Generator-p`, just as the equation reads:
""",
)

code(
    "lhs",
    """
alpha = 0.7
g = m.variables["Generator-p"]
w = n.snapshot_weightings.generators
res = n.generators.index[n.generators.carrier.isin(["onwind", "offwind", "solar"])]

lhs = (g.sel(name=res) * w).sum()
rhs = alpha * (g * w).sum()
m.add_constraints(lhs >= rhs, name="RES-share")
""",
)

md(
    "export-note",
    """
:::{warning}
`export_to_netcdf` saves the components and the results, not the linopy model. A custom constraint is lost when you save and reload the network: add it again after `create_model()`, as Task 4 does. A `GlobalConstraint` (Task 3) is a component, so it is saved. See [PyPSA issue #2014](https://github.com/PyPSA/PyPSA/issues/2014).
:::
""",
)

md(
    "solve-md",
    "`solve_model` solves the model and writes the results back into `n`, as `n.optimize()` does:",
)

code("solve", 'n.optimize.solve_model(io_api="direct")')

code("objective4", "n.objective / 1e9")

md(
    "dual-md",
    """
As for the CO₂ limit of Task 3, the solver returns a **dual value** for each constraint. The sign follows the sense of the constraint. For a `>=` constraint, such as this renewable share, a larger right-hand side tightens it and raises the cost, so the dual is positive. Here the dual $\\mu$ is in €/MWh:
""",
)

code("dual", 'm.constraints["RES-share"].dual')

md(
    "pdc-md",
    "The dual of the energy balance is the electricity price, stored in `n.buses_t.marginal_price` (€/MWh). The price duration curve sorts the German prices from high to low:",
)

code(
    "pdc",
    """
step3 = pypsa.Network("network-step3.nc")
pdc = pd.DataFrame(
    {
        "Step 3": step3.buses_t.marginal_price["DE"].sort_values(ascending=False).values,
        "α = 0.7": n.buses_t.marginal_price["DE"].sort_values(ascending=False).values,
    }
)
pdc.plot(title="Price duration curve, Germany", xlabel="snapshots, sorted", ylabel="€/MWh", ylim=(-25, 200))
""",
)

md(
    "pdc-levels",
    """
Each flat level of the curve is the marginal cost of the technology that sets the price (6 h averages):

- **Step 3.** OCGT sets the price most of the time, at its marginal cost $o_\\text{OCGT}$ of 82.4 €/MWh. Near 0 €/MWh, curtailed wind and solar set it. Above, OCGT runs at full capacity and the electrolysis sets the price by cutting its consumption.
- **$\\alpha = 0.7$.** With all terms on the left, the constraint reads $(1 - \\alpha) \\sum_{t} w_t \\sum_{s \\in \\text{RES}} g_{s,t} - \\alpha \\sum_{t} w_t \\sum_{s \\not\\in \\text{RES}} g_{s,t} \\geq 0$. Each MWh of wind or solar counts $1 - \\alpha$, each MWh of OCGT counts $-\\alpha$. The constraint thus acts as a tax on OCGT and a subsidy for wind and solar, both set by the dual $\\mu$ = 35.1 €/MWh. OCGT now sets the price at $o_\\text{OCGT} + \\alpha \\mu \\approx 107$ €/MWh, and curtailed wind and solar at $-(1 - \\alpha) \\mu \\approx -10.5$ €/MWh.
""",
)

md(
    "task4",
    f"""
## Task 4 · A higher renewable share (if time allows)

**7 min**

Rebuild the model from `network-step3.nc` with $\\alpha = 0.75$ and solve it. How do the dual value, the system cost and the electricity prices change? Add the German prices at $\\alpha = 0.75$ to the price duration curve.

:::{{hint}}
Repeat the three calls of this step: `create_model()`, `add_constraints(...)`, `solve_model()`. Add a column to the `pdc` table, sorted like the others, and plot it again.
:::

*Source: [Linopy]({LP}), Exercises.*
""",
)

code("task4-code", "# Your code here")

# ================================================================ close
md(
    "recap",
    f"""
# What you did today

| | Step | Learning objective |
|---|---|---|
| ✓ | 1 · Capacity expansion for Germany | Build a model with `Network`, `Bus`, `Load`, `Generator`, `StorageUnit` |
| ✓ | 2 · Sector coupling with hydrogen | Couple sectors with `Process`, `Link` and `Store` |
| ✓ | 3 · Parameters as constraints, and the grid | Define behaviour with parameters; add `Line`s |
| ✓ | 4 · Under the hood: linopy | Read the optimisation problem, add a constraint, read its dual |

**Further learning.** Heat and transport in [PyPSA: Sector-Coupling]({SC}). The full course: [Data Science for Energy System Modelling]({DSESM}/intro/).
""",
)

# ================================================================ solutions
md(
    "solutions",
    """
# Solutions

:::{warning}
Try the tasks first.
:::
""",
)

md("sol1-md", "## Task 1 · Only wind or only solar")

code(
    "sol1",
    """
n_task = pypsa.Network("network-step1.nc")
n_task.remove("Generator", ["DE onwind", "DE offwind"])
n_task.optimize(io_api="direct")
n_task.statistics.optimal_capacity().div(1e3)  # GW
""",
)

code("sol1-cost", "n_task.objective / 1e9")

md(
    "sol1-text",
    "**Interpretation** (6 h averages). Without wind, the system cost rises from 44.3 to 50.2 bn€/a (+13 %). The model replaces 75 GW of offshore wind with more solar (133 → 220 GW) and more OCGT (74 → 85 GW). OCGT output more than doubles, from 190 to 413 TWh. The battery shrinks from 17 to 4.1 GW. Removing solar instead gives a similar picture, with a smaller cost increase.",
)

md("sol2-md", "## Task 2 · Expensive hydrogen storage")

code(
    "sol2",
    """
n_task = pypsa.Network("network-step2.nc")
n_task.stores.loc["DE hydrogen storage", "capital_cost"] *= 10
n_task.optimize(io_api="direct")
n_task.statistics.optimal_capacity().div(1e3)  # GW, GWh
""",
)

code("sol2-cost", "n_task.objective / 1e9")

md(
    "sol2-text",
    "**Interpretation** (6 h averages). Hydrogen storage halves, from 0.55 to 0.28 TWh, and the system cost rises only from 62.3 to 62.7 bn€/a (+0.7 %). The storage of Step 2 is already small: the electrolysis runs at 94 % of its capacity on average and follows the constant demand. Without cheap storage, the model builds more OCGT (77 → 84 GW), and OCGT output grows from 254 to 267 TWh. The battery disappears (11 → 0 GW).",
)

md("sol3-md", "## Task 3 · A CO₂ limit and its price")

code(
    "sol3",
    """
n_task = pypsa.Network("network-step3.nc")
n_task.add(
    "GlobalConstraint",
    "CO2Limit",
    carrier_attribute="co2_emissions",
    sense="<=",
    constant=0.7 * co2,  # t
)
n_task.optimize(io_api="direct")
n_task.global_constraints.mu  # €/t
""",
)

code("sol3-cost", "n_task.objective / 1e9")

code(
    "sol3-capacity",
    """
n_task.statistics.optimal_capacity(groupby=["bus", "carrier"]).div(1e3)  # GW, GWh
""",
)

md(
    "sol3-text",
    "**Interpretation** (6 h averages). Cutting the emissions by 30 %, from 156 to 109 Mt, gives a CO₂ price of 86 €/t (`mu` is −86): the marginal abatement cost. The system cost rises by 3.4 %, from 73.8 to 76.3 bn€/a. German onshore wind replaces much of the OCGT output. More electrolysis and hydrogen storage absorb the wind peaks, and the lines grow. The TYNDP 2026 National Trends+ CO₂ price for 2035, 197.5 €/t, is a scenario input for the whole EU ETS. Ours is a result: the cost of a 30 % cut in a stylised model of three countries.",
)

md("sol4-md", "## Task 4 · A higher renewable share (if time allows)")

code(
    "sol4",
    """
n_task = pypsa.Network("network-step3.nc")
m_task = n_task.optimize.create_model()
g = m_task.variables["Generator-p"]

lhs = (g.sel(name=res) * w).sum()
rhs = 0.75 * (g * w).sum()
m_task.add_constraints(lhs >= rhs, name="RES-share")
n_task.optimize.solve_model(io_api="direct")
m_task.constraints["RES-share"].dual
""",
)

code("sol4-cost", "n_task.objective / 1e9")

code(
    "sol4-pdc",
    """
pdc["α = 0.75"] = n_task.buses_t.marginal_price["DE"].sort_values(ascending=False).values
pdc.plot(title="Price duration curve, Germany", xlabel="snapshots, sorted", ylabel="€/MWh", ylim=(-25, 200))
""",
)

md("sol4-capacity-md", "The capacities show where the extra cost goes:")

code(
    "sol4-plot",
    """
networks = {"Step 3": step3, "α = 0.7": n, "α = 0.75": n_task}
capacity = pd.DataFrame(
    {label: nw.statistics.optimal_capacity().drop("Store") for label, nw in networks.items()}
)
capacity.droplevel("component").div(1e3).plot.bar(title="Capacity", ylabel="GW", rot=0)
""",
)

md(
    "sol4-text",
    "**Interpretation** (6 h averages). The dual rises from 35 €/MWh at $\\alpha = 0.7$ to 60 €/MWh at $\\alpha = 0.75$. The system cost rises from 75.4 to 77.4 bn€/a, against 73.8 bn€/a in Step 3. Each extra percent of renewables costs more than the one before. The price levels move with the dual: OCGT now sets $82.4 + 0.75 \\times 60 \\approx 127$ €/MWh, and wind and solar $o_s - 0.25 \\times 60 \\approx -15$ €/MWh. The capacities show how: OCGT falls from 102 GW in Step 3 to 90 and 86 GW. Onshore wind (all three countries) grows from 95 to 150 and 166 GW: at $\\alpha = 0.75$, all wind and solar reach their limits. The battery (0 → 18 → 24 GW) and the electrolysis (24 → 29 → 42 GW) grow too: they use wind and solar output that would otherwise be curtailed. The lines grow from 10 to 13 GW. The battery result depends on the resolution: at 3 h, Step 3 already builds 20 GW of battery.",
)

# ================================================================ sources
md(
    "sources",
    f"""
# Sources and licences

| Source | Used in | Licence |
|---|---|---|
| [Data Science for Energy System Modelling]({DSESM}/intro/), F. Neumann, TU Berlin: [PyPSA: Capacity Expansion]({CEM}), [PyPSA: Sector-Coupling]({SC}), [Linopy]({LP}) | structure, equations, code, Tasks 1–4 | MIT (code), CC-BY-4.0 (content) |
| [PyPSA](https://github.com/PyPSA/PyPSA) and its [user guide]({UG}/optimization/overview/) | all steps | MIT (code), CC-BY-4.0 (docs) |
| PyPSA examples [capacity expansion planning](https://docs.pypsa.org/latest/examples/capacity-expansion-planning-single-node/) and [sector coupling](https://docs.pypsa.org/latest/examples/sector-coupling-single-node/) | Steps 1–2 | CC-BY-4.0 (code and text) |
| [linopy](https://github.com/PyPSA/linopy) | Step 4 | MIT |
| [PyPSA/technology-data](https://github.com/PyPSA/technology-data) v0.15.0, `costs_2035.csv` | costs | code GPL-3.0; output files: licence not stated |
| [Open-TYNDP]({OTYNDP}), OET, branch `tyndp-2026`, `data/custom_costs.csv` | overwrites based on TYNDP 2026, choice of weather scenario | code MIT; `custom_costs.csv` CC-BY-4.0 |
| ENTSO-E and ENTSOG, [TYNDP 2026 Scenarios data]({TYNDP}), National Trends+ 2035, weather scenario WS032: electricity demand (`Demand/2035/ELECTRICITY_MARKET 2035.xlsx`), PECD capacity factors (`PECD/2035/`), PEMMDB 2.X, KPI dashboard, CO₂ price (`TYNDP2026Scenarios_Fuel_CO2_Prices.xlsx`); extracted, rounded and converted to MW in `data/tyndp2026-nt2035-hourly-demand-wind-solar.csv` and `data/tyndp2026-nt2035-wind-solar-capacity.csv` | demand, capacity factors, hydrogen demand, `p_nom_max`, CO₂ price in Task 3 | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
""",
)

nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbformat.validate(nb)
nbformat.write(nb, OUT)
print(f"wrote {OUT} ({len(cells)} cells, resolution {RESOLUTION} h)")
