"""Model Initialisation

We build a capacity expansion model for Germany, Austria and Switzerland in 2035,
with one node per country, connected by AC lines. Germany also has a hydrogen demand,
served by electrolysis, a fuel cell and hydrogen storage.

The wind and solar capacities are capped at the TYNDP 2026 National Trends+ 2035 fleet,
and a CO2 limit caps the emissions.

"""

import os
import pypsa
import pandas as pd

# %%
pypsa.options.params.optimize.include_objective_constant = False

# Must match the resolution in 3_get_timeseries.py
RESOLUTION = 6


def main(
    costs: pd.DataFrame,
    ts: pd.DataFrame,
    p_nom_max: pd.Series,
    CO2_constraint: float = 120e6,
) -> pypsa.Network:
    """For building the model, we start again by initialising an empty network.

    Arguments
    ---------
    costs: pd.DataFrame
        Cost and other technology data
    ts: pd.DataFrame
        Timeseries data
    p_nom_max: pd.Series
        Maximum wind and solar capacity per generator, in MW
    CO2_constraint: float
        CO2 limit, in t/a

    Returns
    -------
    pypsa.Network
        Initialised PyPSA Network

    """

    n = pypsa.Network()

    # The snapshots of the model are the time series index, each representing RESOLUTION hours.

    n.snapshots = ts.index
    n.snapshot_weightings.loc[:, :] = RESOLUTION

    # ## Adding Components

    # Then, we add all the technologies we are going to include as carriers.

    carriers = {
        "onwind": "dodgerblue",
        "offwind": "navy",
        "solar": "gold",
        "OCGT": "indianred",  # open cycle gas turbine
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

    # Each country gets an electricity bus, a demand and an OCGT.

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

    # Adding the variable renewable generators works almost identically, but we also need to
    # supply the capacity factors via `p_max_pu` and the capacity limits via `p_nom_max`.

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

    n.add(
        "GlobalConstraint",
        "CO2Limit",
        carrier_attribute="co2_emissions",
        sense="<=",
        constant=CO2_constraint,
    )

    return n


if __name__ == "__main__":

    cost_data_path = os.path.join("data", "costs.csv")
    cost_data = pd.read_csv(cost_data_path, index_col=[0])

    timeseries_data_path = os.path.join("data", "timeseries.csv")
    timeseries_data = pd.read_csv(timeseries_data_path, index_col=0, parse_dates=True)

    p_nom_max_path = os.path.join("data", "tyndp2026-nt2035-wind-solar-capacity.csv")
    p_nom_max_data = pd.read_csv(p_nom_max_path, index_col=0).p_nom_max

    network = main(cost_data, timeseries_data, p_nom_max_data)

    network_path = os.path.join("results", "cem.nc")
    network.export_to_netcdf(network_path)
