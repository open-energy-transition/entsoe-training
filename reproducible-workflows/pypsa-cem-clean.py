"""PyPSA capacity expansion model: single-node Germany, 2030 costs, 2015 weather."""

import matplotlib.pyplot as plt
import pandas as pd
import pypsa
from pypsa.costs import annuity

pd.options.plotting.backend = "plotly"
pypsa.options.params.optimize.include_objective_constant = True

year = 2030

# 1. Read data
costs = pd.read_csv(
    f"https://raw.githubusercontent.com/PyPSA/technology-data/master/outputs/costs_{year}.csv",
    index_col=[0, 1],
)
ts = pd.read_csv(
    "https://tubcloud.tu-berlin.de/s/pKttFadrbTKSJKF/download/time-series-lecture-2.csv",
    index_col=0,
    parse_dates=True,
)

# 2. Process data

# Technology costs: convert units, fill defaults, pivot to technology x parameter
costs.loc[costs.unit.str.contains("/kW"), "value"] *= 1e3
costs.unit = costs.unit.str.replace("/kW", "/MW")

defaults = {
    "FOM": 0,
    "VOM": 0,
    "efficiency": 1,
    "fuel": 0,
    "investment": 0,
    "lifetime": 25,
    "CO2 intensity": 0,
    "discount rate": 0.07,
}
costs = costs.value.unstack().fillna(defaults)

for tech in ["OCGT", "CCGT"]:
    costs.at[tech, "fuel"] = costs.at["gas", "fuel"]
    costs.at[tech, "CO2 intensity"] = costs.at["gas", "CO2 intensity"]

# Marginal cost (EUR/MWh) and annualised capital cost (EUR/MW/a)
costs["marginal_cost"] = costs["VOM"] + costs["fuel"] / costs["efficiency"]
annuity_factor = annuity(costs["discount rate"], costs["lifetime"])
costs["capital_cost"] = (annuity_factor + costs["FOM"] / 100) * costs["investment"]

# Time series: load GW -> MW, downsample resolution
ts.load *= 1e3
resolution = 4  
ts = ts.resample(f"{resolution}h").first()


# 3. Build network

n = pypsa.Network()
n.set_snapshots(ts.index)
n.snapshot_weightings.loc[:, :] = resolution

n.add("Bus", "electricity", carrier="electricity")

carriers = {
    "onwind": "dodgerblue",
    "offwind": "aquamarine",
    "solar": "gold",
    "OCGT": "indianred",
    "hydrogen storage underground": "magenta",
    "battery storage": "yellowgreen",
    "electricity": "black",
}
n.add(
    "Carrier",
    list(carriers),
    color=list(carriers.values()),
    co2_emissions=[
        costs.at[c, "CO2 intensity"] if c in costs.index else 0 for c in carriers
    ],
)

n.add("Load", "demand", bus="electricity", p_set=ts.load)

# Dispatchable generation
n.add(
    "Generator",
    "OCGT",
    bus="electricity",
    carrier="OCGT",
    capital_cost=costs.at["OCGT", "capital_cost"],
    marginal_cost=costs.at["OCGT", "marginal_cost"],
    efficiency=costs.at["OCGT", "efficiency"],
    p_nom_extendable=True,
)

# Variable renewables
for tech in ["onwind", "offwind", "solar"]:
    n.add(
        "Generator",
        tech,
        bus="electricity",
        carrier=tech,
        p_max_pu=ts[tech],
        capital_cost=costs.at[tech, "capital_cost"],
        marginal_cost=costs.at[tech, "marginal_cost"],
        efficiency=costs.at[tech, "efficiency"],
        p_nom_extendable=True,
    )

# Short-term storage: battery, 4 h energy-to-power ratio
n.add(
    "StorageUnit",
    "battery storage",
    bus="electricity",
    carrier="battery storage",
    max_hours=4,
    capital_cost=costs.at["battery inverter", "capital_cost"]
    + 4 * costs.at["battery storage", "capital_cost"],
    efficiency_store=costs.at["battery inverter", "efficiency"],
    efficiency_dispatch=costs.at["battery inverter", "efficiency"],
    p_nom_extendable=True,
    cyclic_state_of_charge=True,
)

# Long-term storage: hydrogen, 336 h energy-to-power ratio
n.add(
    "StorageUnit",
    "hydrogen storage underground",
    bus="electricity",
    carrier="hydrogen storage underground",
    max_hours=336,
    capital_cost=costs.at["electrolysis", "capital_cost"]
    + costs.at["fuel cell", "capital_cost"]
    + 336 * costs.at["hydrogen storage underground", "capital_cost"],
    efficiency_store=costs.at["electrolysis", "efficiency"],
    efficiency_dispatch=costs.at["fuel cell", "efficiency"],
    p_nom_extendable=True,
    cyclic_state_of_charge=True,
)

# 100% renewable: zero CO2 emissions
n.add(
    "GlobalConstraint",
    "CO2Limit",
    carrier_attribute="co2_emissions",
    sense="<=",
    constant=0,
)


# 4. Solve

n.optimize(log_to_console=False)

# 5. Results and plots


print(f"Total system cost: {n.objective / 1e9:.2f} bn EUR/a")
print("\nOptimal capacities [GW]:\n", n.statistics.optimal_capacity().div(1e3))
print("\nEnergy balance [TWh]:\n", n.statistics.energy_balance().sort_values().div(1e6))

tsc = (
    pd.concat({"capex": n.statistics.capex(), "opex": n.statistics.opex()}, axis=1)
    .div(1e9)
    .round(2)
)
print("\nSystem cost [bn EUR/a]:\n", tsc)

demand = n.snapshot_weightings.generators @ n.loads_t.p_set.sum(axis=1)
print(f"\nCost per MWh consumed: {tsc.sum().sum() * 1e9 / demand:.2f} EUR/MWh")

n.statistics.energy_balance.iplot().show()

n.buses_t.marginal_price.plot(labels=dict(value="Electricity Price [EUR/MWh]")).show()

pdc = n.buses_t.marginal_price.sort_values(
    by="electricity", ascending=False
).reset_index(drop=True)
pdc.index = [i * resolution / 8760 * 100 for i in range(len(pdc))]
pdc.plot(
    labels=dict(value="Electricity Price [EUR/MWh]", index="Percentage of time [%]")
).show()

# 6. Sensitivity: system cost vs CO2 limit

sensitivity = {}
for co2 in [150, 100, 50, 25, 0]:
    n.global_constraints.loc["CO2Limit", "constant"] = co2 * 1e6
    n.optimize(solver_name="highs", log_to_console=False)
    sensitivity[co2] = (
        pd.concat([n.statistics.capex(), n.statistics.opex()])
        .groupby("carrier")
        .sum()
        .div(1e9)
    )

df = pd.DataFrame(sensitivity).T
df.plot.area(
    stacked=True,
    linewidth=0,
    color=df.columns.map(n.carriers.color),
    figsize=(4, 4),
    xlim=(0, 150),
    xlabel=r"CO$_2$ emissions [Mt/a]",
    ylabel="System cost [bn EUR/a]",
    ylim=(0, 80),
    backend="matplotlib",
)
plt.legend(frameon=False, loc=(1.05, 0))
plt.tight_layout()
plt.show()
