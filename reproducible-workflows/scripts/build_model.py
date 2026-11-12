"""Model Initialisation

See also https://model.energy.

**In this section, we will build a replica of [model.energy](https://model.energy).**
This tool calculates the cost of meeting a constant electricity demand from a combination
of wind power, solar power and storage for different regions of the world.

We deviate from [model.energy](https://model.energy) by including offshore wind generation
and electricity demand profiles rather than a constant electricity demand. Also, we are going
to start with Germany only. You can adapt the code to other countries as an exercise.

"""

import os
import pypsa
import pandas as pd

# %%
pypsa.options.params.optimize.include_objective_constant = True

RESOLUTION = 4


def main(
    costs: pd.DataFrame, ts: pd.DataFrame, CO2_constraint: float = 0
) -> pypsa.Network:
    """For building the model, we start again by initialising an empty network.

    Arguments
    ---------
    costs: pd.DataFrame
        Cost and other technology data
    ts: pd.DataFrame
        Timeseries data

    Returns
    -------
    pypsa.Network
        Initialised PyPSA Network

    """

    n = pypsa.Network()

    # Then, we add a single bus...

    n.add("Bus", "electricity", carrier="electricity")

    # ...and tell the `pypsa.Network` object `n` that the [snapshots](https://docs.pypsa.org/latest/user-guide/design/#snapshots) of the model will be taken from the time series index `ts.index`.

    n.snapshots = ts.index

    n.snapshots[:12]

    # The [weighting of the snapshots](https://docs.pypsa.org/latest/user-guide/design/#snapshots) (e.g. how many hours they represent, see $w_t$ in problem formulation above) can be set in `n.snapshot_weightings`.

    n.snapshot_weightings.head(2)

    n.snapshot_weightings.loc[:, :] = RESOLUTION

    n.snapshot_weightings.head(2)

    # ## Adding Components

    # Then, we add all the technologies we are going to include as carriers.

    carriers = [
        "onwind",
        "offwind",
        "solar",
        "OCGT",  # open cycle gas turbine
        "hydrogen storage underground",
        "battery storage",
        "electricity",
    ]

    n.add(
        "Carrier",
        carriers,
        color=[
            "dodgerblue",
            "aquamarine",
            "gold",
            "indianred",
            "magenta",
            "yellowgreen",
            "black",
        ],
        co2_emissions=[
            costs.at[c, "CO2 intensity"] if c in costs.index else 0 for c in carriers
        ],
    )

    # Next, we add the demand time series to the model.

    n.add(
        "Load",
        "demand",
        bus="electricity",
        p_set=ts.load,
    )

    # We are going to add one dispatchable generation technology to the model. This is an open-cycle gas turbine (OCGT) with CO$_2$ emissions of 0.2 t/MWh$_{th}$.

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

    # Adding the variable renewable generators works almost identically, but we also need to
    # supply the capacity factors to the model via the attribute `p_max_pu`.

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
    capital_costs = (
        costs.at["electrolysis", "capital_cost"]
        + costs.at["fuel cell", "capital_cost"]
        + 336 * costs.at["hydrogen storage underground", "capital_cost"]
    )

    n.add(
        "StorageUnit",
        "hydrogen storage underground",
        bus="electricity",
        carrier="hydrogen storage underground",
        max_hours=336,
        capital_cost=capital_costs,
        efficiency_store=costs.at["electrolysis", "efficiency"],
        efficiency_dispatch=costs.at["fuel cell", "efficiency"],
        p_nom_extendable=True,
        cyclic_state_of_charge=True,
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

    network = main(cost_data, timeseries_data)

    network_path = os.path.join("results", "cem.nc")
    network.export_to_netcdf(network_path)
