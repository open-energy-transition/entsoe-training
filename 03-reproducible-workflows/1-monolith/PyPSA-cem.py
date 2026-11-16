"""PyPSA capacity expansion model: Germany, 2035 costs, TYNDP 2026 data.

The model of Step 3 and Task 3 (CO2 limit) of the "Hands on with PyPSA components" notebook,
as one monolithic script.

Run from 03-reproducible-workflows: python 1-monolith/PyPSA-cem.py
"""

import logging

import matplotlib.pyplot as plt
import pandas as pd
import pypsa
from pypsa.costs import annuity

logging.basicConfig(level=logging.WARNING)
pypsa.options.params.optimize.log_to_console = False
pypsa.options.api.legacy_string_dtype = False
pypsa.options.params.optimize.include_objective_constant = False

year = 2035

# 1. Read data
data_dir = "../02-hands-on-pypsa/data"
costs = pd.read_csv(
    f"https://raw.githubusercontent.com/PyPSA/technology-data/v0.15.0/outputs/costs_{year}.csv",
    index_col=[0, 1],
)
ts = pd.read_csv(
    f"{data_dir}/tyndp2026-nt2035-hourly-demand-wind-solar.csv",
    index_col=0,
    parse_dates=True,
)
p_nom_max = pd.read_csv(
    f"{data_dir}/tyndp2026-nt2035-wind-solar-capacity.csv", index_col=0
).p_nom_max

# 2. Process cost and timeseries data

# Technology costs: convert units, fill defaults, pivot to technology x parameter
costs.loc[costs.unit.str.contains("/kW"), "value"] *= 1e3
costs.unit = costs.unit.str.replace("/kW", "/MW")

defaults = {
    "FOM": 0,
    "VOM": 0,
    "efficiency": 1,
    "fuel": 0,
    "investment": 0,
    "CO2 intensity": 0,
    "discount rate": 0.07,
}
costs = costs.value.unstack().fillna(defaults)

# Open-TYNDP overwrites, TYNDP 2026 National Trends+ 2035
costs.loc["solar"] = costs.loc["solar-utility"]
costs["lifetime"] = 25
costs.loc["OCGT", ["fuel", "efficiency", "VOM", "CO2 intensity"]] = [33.93, 0.42, 1.6, 0.1744]
costs.at["electrolysis", "efficiency"] = 0.7
costs.loc["hydrogen storage underground", ["investment", "FOM"]] = [1750, 0]
costs.loc[["onwind", "offwind", "solar"], "VOM"] = [0.015, 0.015, 0.01]

# Marginal cost (EUR/MWh) and annualised capital cost (EUR/MW/a)
costs["marginal_cost"] = costs["VOM"] + costs["fuel"] / costs["efficiency"]
annuity_factor = annuity(costs["discount rate"], costs["lifetime"])
costs["capital_cost"] = (annuity_factor + costs["FOM"] / 100) * costs["investment"]

# Time series: average over blocks of `resolution` hours
resolution = 6
ts = ts.resample(f"{resolution}h").mean()


# 3. Build network

n = pypsa.Network()
n.add("Bus", "DE", carrier="AC")
n.snapshots = ts.index
n.snapshot_weightings.loc[:, :] = resolution

carriers = {
    "onwind": "dodgerblue",
    "offwind": "navy",
    "solar": "gold",
    "OCGT": "indianred",
    "battery storage": "yellowgreen",
    "AC": "black",
    "hydrogen": "cyan",
    "electrolysis": "magenta",
    "fuel cell": "orange",
    "hydrogen storage": "purple",
}
n.add(
    "Carrier",
    list(carriers),
    color=list(carriers.values()),
    co2_emissions=[
        costs.at[c, "CO2 intensity"] if c in costs.index else 0 for c in carriers
    ],
)

# Electricity: demand, OCGT, wind and solar
n.add("Load", "DE load", bus="DE", p_set=ts["DE load"])
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

# Variable renewables, capped at the TYNDP 2026 fleet
for tech in ["onwind", "offwind", "solar"]:
    n.add(
        "Generator",
        f"DE {tech}",
        bus="DE",
        carrier=tech,
        p_max_pu=ts[f"DE {tech}"],
        capital_cost=costs.at[tech, "capital_cost"],
        marginal_cost=costs.at[tech, "marginal_cost"],
        p_nom_extendable=True,
        p_nom_max=p_nom_max[f"DE {tech}"],
    )

# Short-term storage: battery, 4 h energy-to-power ratio
max_hours = 4
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

# Hydrogen: electrolysis (Process), fuel cell (Link), storage (Store), demand
n.add("Bus", "DE hydrogen", carrier="hydrogen")
n.add(
    "Process",
    "DE electrolysis",
    bus0="DE",
    bus1="DE hydrogen",
    carrier="electrolysis",
    rate0=-1,
    rate1=costs.at["electrolysis", "efficiency"],
    capital_cost=costs.at["electrolysis", "capital_cost"],
    p_nom_extendable=True,
)
n.add(
    "Link",
    "DE fuel cell",
    bus0="DE hydrogen",
    bus1="DE",
    carrier="fuel cell",
    efficiency=costs.at["fuel cell", "efficiency"],
    capital_cost=costs.at["fuel cell", "capital_cost"],
    p_nom_extendable=True,
)
n.add(
    "Store",
    "DE hydrogen storage",
    bus="DE hydrogen",
    carrier="hydrogen storage",
    capital_cost=costs.at["hydrogen storage underground", "capital_cost"],
    e_nom_extendable=True,
    e_cyclic=True,
)
n.add(
    "Load",
    "DE hydrogen demand",
    bus="DE hydrogen",
    carrier="hydrogen",
    p_set=142.7e6 / 8760,  # 142.7 TWh/a
)

# CO2 limit, for illustration: 70 % of the emissions without limit (132.9 Mt/a), as in Task 3 of the previous session
n.add(
    "GlobalConstraint",
    "CO2Limit",
    carrier_attribute="co2_emissions",
    sense="<=",
    constant=93e6,  # t/a
)


# 4. Solve

n.optimize(io_api="direct")

# 5. Results and plots

co2_per_mwh = n.generators.carrier.map(n.carriers.co2_emissions).div(n.generators.efficiency)
co2 = n.snapshot_weightings.generators @ (n.generators_t.p * co2_per_mwh).sum(axis=1)

print(f"Total system cost: {n.objective / 1e9:.2f} bn EUR/a")
print(f"CO2 emissions: {co2 / 1e6:.1f} Mt/a")
print(f"CO2 price: {-n.global_constraints.mu['CO2Limit']:.2f} EUR/t")
print("\nOptimal capacities [GW, GWh]:\n", n.statistics.optimal_capacity().div(1e3))
print(
    "\nElectricity balance [TWh]:\n",
    n.statistics.energy_balance(bus_carrier="AC").sort_values().div(1e6),
)

fig, ax, _ = n.statistics.optimal_capacity.plot.bar(
    components="Generator", x="carrier", y="value", color="carrier"
)
ax.set(title="Generation capacity, Germany", ylabel="MW")
plt.show()
