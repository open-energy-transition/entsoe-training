"""PyPSA capacity expansion model: Germany, Austria, Switzerland, 2035 costs, TYNDP 2026 data."""

import matplotlib.pyplot as plt
import pandas as pd
import pypsa
from pypsa.costs import annuity

pypsa.options.params.optimize.include_objective_constant = False

year = 2035

# 1. Read data
data_url = "https://raw.githubusercontent.com/open-energy-transition/entsoe-training/feat/pypsa-handson/notebooks/hands-on-with-pypsa/data"
costs = pd.read_csv(
    f"https://raw.githubusercontent.com/PyPSA/technology-data/v0.15.0/outputs/costs_{year}.csv",
    index_col=[0, 1],
)
ts = pd.read_csv(
    f"{data_url}/tyndp2026-nt2035-hourly-demand-wind-solar.csv",
    index_col=0,
    parse_dates=True,
)
p_nom_max = pd.read_csv(
    f"{data_url}/tyndp2026-nt2035-wind-solar-capacity.csv", index_col=0
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
n.set_snapshots(ts.index)
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

# Electricity: one bus per country, with demand, OCGT, wind and solar
for country in ["DE", "AT", "CH"]:
    n.add("Bus", country, carrier="AC", v_nom=380)
    n.add("Load", f"{country} load", bus=country, p_set=ts[f"{country} load"])
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

# Variable renewables, capped at the TYNDP 2026 fleet (offshore wind in Germany only)
for gen in p_nom_max.index:
    country, tech = gen.split()
    n.add(
        "Generator",
        gen,
        bus=country,
        carrier=tech,
        p_max_pu=ts[gen],
        capital_cost=costs.at[tech, "capital_cost"],
        marginal_cost=costs.at[tech, "marginal_cost"],
        p_nom_extendable=True,
        p_nom_max=p_nom_max[gen],
    )

# Short-term storage: battery in Germany, 4 h energy-to-power ratio
n.add(
    "StorageUnit",
    "DE battery storage",
    bus="DE",
    carrier="battery storage",
    max_hours=4,
    capital_cost=costs.at["battery inverter", "capital_cost"]
    + 4 * costs.at["battery storage", "capital_cost"],
    efficiency_store=costs.at["battery inverter", "efficiency"],
    efficiency_dispatch=costs.at["battery inverter", "efficiency"],
    p_nom_extendable=True,
    cyclic_state_of_charge=True,
)

# Hydrogen in Germany: electrolysis (Process), fuel cell (Link), storage (Store), demand
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

# Greenfield AC grid: length in km between country centres
for bus0, bus1, length in [("DE", "AT", 500), ("DE", "CH", 510), ("AT", "CH", 480)]:
    n.add(
        "Line",
        f"{bus0}-{bus1}",
        bus0=bus0,
        bus1=bus1,
        type="Al/St 240/40 4-bundle 380.0",
        length=length,
        capital_cost=costs.at["HVAC overhead", "capital_cost"] * length,
        s_nom_extendable=True,
    )

# CO2 limit of 120 Mt/a
n.add(
    "GlobalConstraint",
    "CO2Limit",
    carrier_attribute="co2_emissions",
    sense="<=",
    constant=120e6,
)


# 4. Solve

n.optimize(log_to_console=False)

# 5. Results and plots

print(f"Total system cost: {n.objective / 1e9:.2f} bn EUR/a")
print(f"CO2 price: {-n.global_constraints.mu['CO2Limit']:.2f} EUR/t")
print("\nOptimal capacities [GW, GWh]:\n",n.statistics.optimal_capacity().div(1e3))
print("\nLine capacities [GW]:\n", n.lines.s_nom_opt.div(1e3))
print(
    "\nElectricity balance [TWh]:\n",
    n.statistics.energy_balance(bus_carrier="AC").sort_values().div(1e6),
)

fig, ax, _ = n.statistics.optimal_capacity.plot.bar(
    components="Generator", x="bus", y="value", color="carrier", stacked=True
)
ax.set(title="Generation capacity per country", ylabel="MW")
plt.show()
