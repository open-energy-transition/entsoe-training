"""Model Initialisation

We build a capacity expansion model for Germany in 2035, with one electricity bus.
Germany also has a hydrogen demand, served by electrolysis, a fuel cell and hydrogen storage.

The wind and solar capacities are capped at the TYNDP 2026 National Trends+ 2035 fleet,
and a CO2 limit caps the emissions. This is the model of Step 3 and Task 3 of the
"Hands on with PyPSA components" notebook.

"""

import os
import pypsa
import pandas as pd

pypsa.options.api.legacy_string_dtype = False

# Must match the resolution in 3_get_timeseries.py
RESOLUTION = 6


def main(
    costs: pd.DataFrame,
    ts: pd.DataFrame,
    p_nom_max: pd.Series,
    CO2_constraint: float = 93e6,  # t/a, 70 % of 132.9 Mt/a, for illustration
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
        CO2 limit, in t/a. The default is 70 % of the emissions without limit
        (132.9 Mt/a), as an illustration, as in Task 3 of the notebook.

    Returns
    -------
    pypsa.Network
        Initialised PyPSA Network

    """

    n = pypsa.Network()
    n.add("Bus", "DE", carrier="AC")

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

    # The electricity bus gets a demand and an OCGT.

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

    # Adding the variable renewable generators works almost identically, but we also need to
    # supply the capacity factors via `p_max_pu` and the capacity limits via `p_nom_max`.

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

    os.makedirs("results", exist_ok=True)
    network_path = os.path.join("results", "cem.nc")
    network.export_to_netcdf(network_path)
